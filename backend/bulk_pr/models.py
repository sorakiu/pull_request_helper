from django.db import models
from django.contrib.auth.models import User


class PRJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    repos = (
        models.JSONField()
    )  # List of repo dicts: [{'id': int, 'name': str, 'owner': str}]
    source_branch = models.CharField(max_length=255, default="main")
    dest_branch = models.CharField(max_length=255)
    pr_title = models.CharField(max_length=255)
    pr_body = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, default="pending"
    )  # pending, processing, completed, failed
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    results = models.JSONField(default=dict)  # Store PR URLs or errors per repo
