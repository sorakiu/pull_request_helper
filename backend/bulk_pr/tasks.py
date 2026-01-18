import logging
import json
from github import Github, Auth, GithubException
from celery import shared_task
from .models import PRJob
from allauth.socialaccount.models import SocialToken

logger = logging.getLogger(__name__)


@shared_task
def create_bulk_prs(job_id):
    try:
        logger.info(f"Starting create_bulk_prs for job_id={job_id}")
        
        job = PRJob.objects.get(id=job_id)
        logger.info(f"Job found: {job.id}, repos={job.repos}, source={job.source_branch}, dest={job.dest_branch}")
        
        job.status = "processing"
        job.save()

        social_token = SocialToken.objects.get(
            account__user=job.user, account__provider="github"
        )
        logger.info(f"GitHub token found for user {job.user.username}")
        
        # Initialize PyGithub client with OAuth token
        auth = Auth.Token(social_token.token)
        g = Github(auth=auth)
        
        # Fetch user's repos from GitHub
        user = g.get_user()
        all_repos = user.get_repos()
        logger.info(f"Fetched repos from GitHub for user {user.login}")
        
        # Build a map of repo ID to repo object
        repo_map = {repo.id: repo for repo in all_repos}
        
        results = {}

        for repo_id in job.repos:
            logger.info(f"Processing repo ID: {repo_id}")
            try:
                if repo_id not in repo_map:
                    raise ValueError(f"Repo ID {repo_id} not found in user's repos")
                
                repo = repo_map[repo_id]
                repo_owner = repo.owner.login
                repo_name = repo.name
                logger.info(f"Repo details: {repo_owner}/{repo_name}")
                logger.info(f"Repo permissions: admin={repo.permissions.admin}, push={repo.permissions.push}, pull={repo.permissions.pull}")
                logger.info(f"Repo private: {repo.private}")
                logger.info(f"Repo has_issues: {repo.has_issues}, has_projects: {repo.has_projects}")
                
                # Check if repository is archived (PRs cannot be created on archived repos)
                if repo.archived:
                    logger.warning(f"Repository {repo_owner}/{repo_name} is archived - PRs cannot be created")
                
                # Check if branches exist
                for branch_name in [job.source_branch, job.dest_branch]:
                    try:
                        branch = repo.get_branch(branch_name)
                        logger.info(f"Branch '{branch_name}' found in {repo_owner}/{repo_name}")
                    except GithubException as e:
                        if e.status == 404:
                            raise ValueError(f"Branch '{branch_name}' not found in {repo_owner}/{repo_name}")
                        raise
                
                # Create PR via PyGithub
                pr_title = job.pr_title
                pr_body = job.pr_body or ""
                logger.info(f"Creating PR: title='{pr_title}', head={job.source_branch}, base={job.dest_branch}")
                
                pr = repo.create_pull(
                    title=pr_title,
                    body=pr_body,
                    head=job.source_branch,
                    base=job.dest_branch,
                )
                logger.info(f"PR created successfully: {pr.html_url}")
                results[repo_id] = {"url": pr.html_url, "number": pr.number}
                
            except (GithubException, ValueError) as e:
                logger.error(f"Error processing repo {repo_id}: {str(e)}", exc_info=True)
                results[repo_id] = {"error": str(e)}

        job.results = results
        job.status = "completed"
        job.save()
        logger.info(f"Job {job_id} completed. Results: {results}")
        
    except Exception as e:
        logger.error(f"Error in create_bulk_prs: {str(e)}", exc_info=True)
        job.status = "failed"
        job.results = {"error": str(e)}
        job.save()
