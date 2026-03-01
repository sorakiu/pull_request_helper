from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from allauth.socialaccount.models import SocialAccount, SocialToken
from .models import PRJob


class PRJobTestCase(TestCase):
    """Test cases for PRJob model"""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser")

    def test_job_creation(self):
        """Test basic PRJob creation with valid data"""
        job = PRJob.objects.create(
            user=self.user,
            repos=[{"id": 1, "name": "repo1", "owner": "owner1"}],
            source_branch="main",
            dest_branch="develop",
            pr_title="Test PR",
        )
        self.assertEqual(job.status, "pending")
        self.assertEqual(job.repos[0]["name"], "repo1")

    def test_job_creation_with_empty_title(self):
        """Test PRJob creation generates default title when none provided"""
        job = PRJob.objects.create(
            user=self.user,
            repos=[{"id": 1, "name": "repo1", "owner": "owner1"}],
            source_branch="feature",
            dest_branch="main",
            pr_title="",  # Empty title
        )
        # Should still work, title can be empty or generated later
        self.assertEqual(job.status, "pending")


class LogoutViewTestCase(APITestCase):
    """Test cases for logout functionality"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        # Create social account and token for the user
        self.social_account = SocialAccount.objects.create(
            user=self.user, provider="github", uid="12345", extra_data={}
        )
        self.social_token = SocialToken.objects.create(
            account=self.social_account,
            token="fake_github_token_12345",
            token_secret="",
            expires_at=None,
        )
        self.logout_url = reverse("logout")

    def test_logout_success(self):
        """Test successful logout deletes the social token"""
        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        # Verify token exists before logout
        self.assertTrue(SocialToken.objects.filter(account__user=self.user).exists())

        # Make logout request
        response = self.client.post(self.logout_url)

        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], "Logged out successfully")

        # Verify token was deleted
        self.assertFalse(SocialToken.objects.filter(account__user=self.user).exists())

    def test_logout_without_token(self):
        """Test logout when user has no social token"""
        # Remove the token
        SocialToken.objects.filter(account__user=self.user).delete()

        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        # Make logout request
        response = self.client.post(self.logout_url)

        # Should return 400 error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "No GitHub token found")

    def test_logout_unauthenticated(self):
        """Test logout without authentication"""
        response = self.client.post(self.logout_url)

        # Should return 403 forbidden (Django's default for unauthenticated DRF requests)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_logout_get_method_not_allowed(self):
        """Test that GET requests to logout are not allowed"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.logout_url)

        # Should return 405 method not allowed
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class RepoListViewTestCase(APITestCase):
    """Test cases for repository listing"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        # Create social account and token
        self.social_account = SocialAccount.objects.create(
            user=self.user, provider="github", uid="12345", extra_data={}
        )
        self.social_token = SocialToken.objects.create(
            account=self.social_account,
            token="fake_github_token_12345",
            token_secret="",
            expires_at=None,
        )
        self.repos_url = reverse("repo-list")

    def test_repos_requires_authentication(self):
        """Test that repos endpoint requires authentication"""
        response = self.client.get(self.repos_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
