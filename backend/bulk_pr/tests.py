from django.test import TestCase
from django.contrib.auth.models import User
from .models import PRJob


class PRJobTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser")

    def test_job_creation(self):
        job = PRJob.objects.create(
            user=self.user,
            repos=[{"id": 1, "name": "repo1", "owner": "owner1"}],
            source_branch="main",
            dest_branch="develop",
            pr_title="Test PR",
        )
        self.assertEqual(job.status, "pending")
        self.assertEqual(job.repos[0]["name"], "repo1")
