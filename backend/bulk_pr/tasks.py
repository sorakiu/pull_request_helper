import logging
import json
import requests
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
        
        headers = {"Authorization": f"token {social_token.token}"}
        
        # Check token scopes
        user_response = requests.get("https://api.github.com/user", headers=headers)
        logger.info(f"Token scopes: {user_response.headers.get('x-oauth-scopes', 'Not available')}")
        
        # Fetch user's repos from GitHub to get full details (owner/name)
        repos_response = requests.get(
            "https://api.github.com/user/repos",
            headers=headers,
        )
        repos_response.raise_for_status()
        all_repos = repos_response.json()
        logger.info(f"Fetched {len(all_repos)} repos from GitHub")
        
        # Build a map of repo ID to repo details
        repo_map = {repo["id"]: repo for repo in all_repos}
        
        results = {}

        for repo_id in job.repos:
            logger.info(f"Processing repo ID: {repo_id}")
            try:
                if repo_id not in repo_map:
                    raise ValueError(f"Repo ID {repo_id} not found in user's repos")
                
                repo_info = repo_map[repo_id]
                repo_owner = repo_info["owner"]["login"]
                repo_name = repo_info["name"]
                logger.info(f"Repo details: {repo_owner}/{repo_name}")
                logger.info(f"Repo permissions: admin={repo_info.get('permissions', {}).get('admin')}, push={repo_info.get('permissions', {}).get('push')}, pull={repo_info.get('permissions', {}).get('pull')}")
                logger.info(f"Repo private: {repo_info.get('private')}")
                logger.info(f"Repo has_issues: {repo_info.get('has_issues')}, has_projects: {repo_info.get('has_projects')}")
                
                # Check if pull requests are enabled (they're usually enabled if has_issues is True or if it's not explicitly disabled)
                if not repo_info.get('has_issues'):
                    logger.warning(f"Pull requests might be disabled on {repo_owner}/{repo_name}")
                
                # Check if branches exist
                for branch in [job.source_branch, job.dest_branch]:
                    branch_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/branches/{branch}"
                    branch_response = requests.get(branch_url, headers=headers)
                    logger.info(f"Branch check {branch}: status {branch_response.status_code}")
                    if branch_response.status_code == 404:
                        raise ValueError(f"Branch '{branch}' not found in {repo_owner}/{repo_name}")
                
                # Create PR via GitHub API
                pr_data = {
                    "title": job.pr_title,
                    "head": job.source_branch,
                    "base": job.dest_branch,
                    "body": job.pr_body or "",
                }
                logger.info(f"PR data: {pr_data}")
                
                url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls"
                logger.info(f"GitHub API URL: {url}")
                logger.info(f"Request headers: {dict(headers)}")
                logger.info(f"Request body (JSON): {json.dumps(pr_data)}")
                
                response = requests.post(
                    url,
                    json=pr_data,
                    headers=headers,
                )
                logger.info(f"GitHub API response status: {response.status_code}")
                logger.info(f"Response headers: {dict(response.headers)}")
                
                # Log full response for debugging
                try:
                    response_json = response.json()
                    logger.info(f"GitHub API response JSON: {response_json}")
                except:
                    logger.info(f"GitHub API response text: {response.text}")
                
                response.raise_for_status()
                pr = response.json()
                results[repo_id] = {"url": pr["html_url"], "number": pr["number"]}
                logger.info(f"PR created successfully: {pr['html_url']}")
                
            except (requests.RequestException, ValueError) as e:
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
