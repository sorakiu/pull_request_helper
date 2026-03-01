import logging
import json
from github import Github, Auth, GithubException
from celery import shared_task
from .models import PRJob
from allauth.socialaccount.models import SocialToken

logger = logging.getLogger(__name__)


class MissingTokenError(Exception):
    """Raised when user's GitHub token is not found."""
    pass


@shared_task
def create_bulk_prs(job_id):
    job = None
    try:
        logger.info(f"Starting bulk PR creation for job {job_id}")

        job = PRJob.objects.get(id=job_id)
        job.status = "processing"
        job.save()

        try:
            social_token = SocialToken.objects.get(
                account__user=job.user, account__provider="github"
            )
        except SocialToken.DoesNotExist:
            raise MissingTokenError("GitHub token not found for user")
        
        # Initialize PyGithub client with OAuth token
        auth = Auth.Token(social_token.token)
        g = Github(auth=auth)
        
        # Fetch user's repos from GitHub
        user = g.get_user()
        all_repos = user.get_repos()
        
        # Build a map of repo ID to repo object
        repo_map = {repo.id: repo for repo in all_repos}
        
        results = {}

        for repo_id in job.repos:
            try:
                if repo_id not in repo_map:
                    raise ValueError(f"Repo ID {repo_id} not found in user's repos")
                
                repo = repo_map[repo_id]
                repo_owner = repo.owner.login
                repo_name = repo.name
                
                # Check if repository is archived (PRs cannot be created on archived repos)
                if repo.archived:
                    raise ValueError(f"Repository {repo_owner}/{repo_name} is archived")
                
                # Check if branches exist
                for branch_name in [job.source_branch, job.dest_branch]:
                    try:
                        repo.get_branch(branch_name)
                    except GithubException as e:
                        if e.status == 404:
                            raise ValueError(f"Branch '{branch_name}' not found in {repo_owner}/{repo_name}") from e
                        raise
                
                # Create PR via PyGithub
                pr = repo.create_pull(
                    title=job.pr_title,
                    body=job.pr_body or "",
                    head=job.source_branch,
                    base=job.dest_branch,
                )
                logger.info(f"PR created: {repo_owner}/{repo_name} #{pr.number}")
                results[repo_id] = {"url": pr.html_url, "number": pr.number}
                
            except (GithubException, ValueError) as e:
                logger.warning(f"Failed to create PR for repo {repo_id}: {e}")
                results[repo_id] = {"error": str(e)}

        job.results = results
        job.status = "completed"
        job.save()
        logger.info(f"Job {job_id} completed: {len([r for r in results.values() if 'url' in r])}/{len(results)} PRs created")
        
    except Exception as e:
        logger.error(f"Error in create_bulk_prs: {str(e)}", exc_info=True)
        if job is not None:
            job.status = "failed"
            job.results = {"error": str(e)}
            job.save()
