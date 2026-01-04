import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from allauth.socialaccount.models import SocialToken
from .models import PRJob
from .tasks import create_bulk_prs


class RepoListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            social_token = SocialToken.objects.get(
                account__user=request.user, account__provider="github"
            )
            headers = {"Authorization": f"token {social_token.token}"}
            response = requests.get(
                "https://api.github.com/user/repos", headers=headers
            )
            response.raise_for_status()
            repos = response.json()
            # Filter to repos user can access, return basic info
            data = [
                {
                    "id": repo["id"],
                    "name": repo["name"],
                    "owner": repo["owner"]["login"],
                }
                for repo in repos
            ]
            return Response(data)
        except SocialToken.DoesNotExist:
            return Response({"error": "GitHub token not found"}, status=400)
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=500)


class JobCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        repos = request.data.get("repos", [])
        source_branch = request.data.get("source_branch", "main")
        dest_branch = request.data.get("dest_branch")
        pr_title = request.data.get("pr_title", f"{source_branch} -> {dest_branch}")
        pr_body = request.data.get("pr_body", "")

        if not repos or not dest_branch:
            return Response({"error": "repos and dest_branch required"}, status=400)

        job = PRJob.objects.create(
            user=request.user,
            repos=repos,
            source_branch=source_branch,
            dest_branch=dest_branch,
            pr_title=pr_title,
            pr_body=pr_body,
        )
        create_bulk_prs.delay(job.id)
        return Response({"job_id": job.id}, status=201)
