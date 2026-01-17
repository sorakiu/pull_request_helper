"""
Views for the bulk PR creation application.

This module contains Django REST Framework views for handling GitHub OAuth,
repository management, and bulk pull request creation jobs.
"""

import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from allauth.socialaccount.models import SocialToken
from .models import PRJob
from .tasks import create_bulk_prs


class RepoListView(APIView):
    """
    API endpoint for listing user's GitHub repositories.

    This view fetches the authenticated user's repositories from GitHub
    using their OAuth token and returns basic repository information.
    Requires authentication.
    """

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


class CSRFTokenView(APIView):
    """
    API endpoint for obtaining CSRF tokens.

    Provides CSRF tokens for single-page application requests.
    This ensures Django's CSRF protection works with React forms.
    No authentication required.
    """

    permission_classes = [AllowAny]

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        """Return CSRF token and set cookie for SPA requests."""
        return Response({"csrfToken": get_token(request)})


class LogoutView(APIView):
    """
    API endpoint for user logout.

    Deletes the user's GitHub OAuth token from the database,
    effectively logging them out. Requires authentication.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Delete the user's GitHub OAuth token.

        This removes the stored token, forcing re-authentication
        on next GitHub API access.
        """
        try:
            # Find and delete the user's GitHub token
            social_token = SocialToken.objects.get(
                account__user=request.user, account__provider="github"
            )
            social_token.delete()
            return Response({"message": "Logged out successfully"})
        except SocialToken.DoesNotExist:
            # Token already deleted or never existed
            return Response({"error": "No GitHub token found"}, status=400)


class JobCreateView(APIView):
    """
    API endpoint for creating bulk pull request jobs.

    Accepts repository IDs, branch names, and PR details to create
    a background job for bulk PR creation. Requires authentication.
    """

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
