import requests
from celery import shared_task
from .models import PRJob
from allauth.socialaccount.models import SocialToken


@shared_task
def create_bulk_prs(job_id):
    try:
        job = PRJob.objects.get(id=job_id)
        job.status = "processing"
        job.save()

        social_token = SocialToken.objects.get(
            account__user=job.user, account__provider="github"
        )
        headers = {"Authorization": f"token {social_token.token}"}
        results = {}

        for repo in job.repos:
            try:
                # Create PR via GitHub API
                pr_data = {
                    "title": job.pr_title,
                    "head": job.source_branch,
                    "base": job.dest_branch,
                    "body": job.pr_body or None,
                }
                response = requests.post(
                    f"https://api.github.com/repos/{repo['owner']}/{repo['name']}/pulls",
                    json=pr_data,
                    headers=headers,
                )
                response.raise_for_status()
                pr = response.json()
                results[repo["id"]] = {"url": pr["html_url"], "number": pr["number"]}
            except requests.RequestException as e:
                results[repo["id"]] = {"error": str(e)}

        job.results = results
        job.status = "completed"
        job.save()
    except Exception as e:
        job.status = "failed"
        job.results = {"error": str(e)}
        job.save()
