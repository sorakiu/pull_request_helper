import logging
from celery import shared_task
from github import Github, Auth, GithubException

from .models import PRJob
from allauth.socialaccount.models import SocialToken

logger = logging.getLogger(__name__)


@shared_task
def create_bulk_prs(job_id):
    job = None
    g = None
    try:
        logger.info(f"Starting create_bulk_prs for job_id={job_id}")

        job = PRJob.objects.get(id=job_id)
        logger.info(
            f"Job found: {job.id}, repos={job.repos}, source={job.source_branch}, dest={job.dest_branch}"
        )

        job.status = "processing"
        job.save()

        social_token = SocialToken.objects.get(
            account__user=job.user, account__provider="github"
        )
        logger.info(f"GitHub token found for user {job.user.username}")

        # Initialize PyGitHub client
        auth = Auth.Token(social_token.token)
        g = Github(auth=auth)

        # Check token scopes and get user info
        user = g.get_user()
        logger.info(f"Authenticated as: {user.login}")

        # For OAuth tokens, scopes might not be available via g.oauth_scopes
        # Check available scopes for debugging purposes
        scopes = getattr(g, "oauth_scopes", []) or []

        # Verify token has required scopes for creating PRs
        has_repo_scope = "repo" in scopes or "public_repo" in scopes
        if not has_repo_scope:
            logger.warning(
                f"Token may be missing required scopes. Has: {scopes}. "
                "Need 'repo' or 'public_repo' scope for creating pull requests. "
                "Please re-authorize the GitHub OAuth app with proper scopes."
            )

        # Fetch user's repos from GitHub to get full details (owner/name)
        all_repos = list(g.get_user().get_repos())
        logger.info(f"Fetched {len(all_repos)} repos from GitHub")

        # Build a map of repo ID to repo details
        repo_map = {repo.id: repo for repo in all_repos}

        results = {}

        for repo_id in job.repos:
            logger.info(f"Processing repo ID: {repo_id}")
            try:
                if repo_id not in repo_map:
                    raise ValueError(f"Repo ID {repo_id} not found in user's repos")

                repo_info = repo_map[repo_id]
                repo_owner = repo_info.owner.login
                repo_name = repo_info.name
                logger.info(f"Repo details: {repo_owner}/{repo_name}")
                permissions = repo_info.permissions
                logger.info(
                    f"Repo permissions: admin={permissions.admin if permissions else None}, push={permissions.push if permissions else None}, pull={permissions.pull if permissions else None}"
                )
                logger.info(f"Repo private: {repo_info.private}")
                logger.info(
                    f"Repo has_issues: {repo_info.has_issues}, has_projects: {repo_info.has_projects}"
                )

                # Check if pull requests are enabled (they're usually enabled if has_issues is True or if it's not explicitly disabled)
                if not repo_info.has_issues:
                    logger.warning(
                        f"Pull requests might be disabled on {repo_owner}/{repo_name}"
                    )

                # Check if branches exist using the repo object from user's repos
                # (repo_info already has proper auth context)
                branch_shas = {}
                for branch in [job.source_branch, job.dest_branch]:
                    try:
                        branch_obj = repo_info.get_branch(branch)
                        branch_shas[branch] = branch_obj.commit.sha
                        logger.info(
                            f"Branch {branch} exists, SHA: {branch_obj.commit.sha}"
                        )
                    except Exception as e:
                        logger.error(f"Branch check {branch} failed: {str(e)}")
                        raise ValueError(
                            f"Branch '{branch}' not found in {repo_owner}/{repo_name}"
                        )

                # Check if branches have the same commit (no diff = can't create PR)
                if branch_shas.get(job.source_branch) == branch_shas.get(
                    job.dest_branch
                ):
                    raise ValueError(
                        f"No differences between {job.source_branch} and {job.dest_branch}. "
                        "Cannot create a pull request without changes."
                    )

                # Fetch the full repository object to ensure we have proper API access
                # The repo from get_repos() may be a partial object
                full_repo = g.get_repo(repo_info.full_name)

                logger.info(
                    f"Creating PR: title={job.pr_title}, head={job.source_branch}, base={job.dest_branch}"
                )
                logger.info(f"Repository API URL: {full_repo.url}")
                logger.info(f"Repository full_name: {full_repo.full_name}")

                pr = full_repo.create_pull(
                    title=job.pr_title,
                    head=job.source_branch,
                    base=job.dest_branch,
                    body=job.pr_body or "",
                )

                results[repo_id] = {"url": pr.html_url, "number": pr.number}
                logger.info(f"PR created successfully: {pr.html_url}")

            except (GithubException, ValueError) as e:
                logger.error(
                    f"Error processing repo {repo_id}: {str(e)}", exc_info=True
                )
                results[repo_id] = {"error": str(e)}

        job.results = results
        job.status = "completed"
        job.save()
        logger.info(f"Job {job_id} completed. Results: {results}")

    except Exception as e:
        logger.error(f"Error in create_bulk_prs: {str(e)}", exc_info=True)
        if job is not None:
            job.status = "failed"
            job.results = {"error": str(e)}
            job.save()
    finally:
        # Close the Github connection to free up resources
        if g is not None:
            g.close()
