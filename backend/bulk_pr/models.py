"""
Database models for the bulk PR creation application.
"""

from django.db import models
from django.contrib.auth.models import User


class PRJob(models.Model):
    """
    Model representing a bulk pull request creation job.

    Each job contains the parameters for creating pull requests across
    multiple GitHub repositories asynchronously.
    """

    # Job configuration
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text="User who created this job"
    )
    repos = models.JSONField(
        help_text="List of GitHub repository IDs: [1234567, 7654321, ...]"
    )
    source_branch = models.CharField(
        max_length=255, default="main", help_text="Branch to create PRs from"
    )
    dest_branch = models.CharField(
        max_length=255, help_text="Branch to create PRs against"
    )

    # PR content
    pr_title = models.CharField(max_length=255, help_text="Title for the pull requests")
    pr_body = models.TextField(
        blank=True, help_text="Description/body for the pull requests"
    )

    # Job status and lifecycle
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        help_text="Current job processing status",
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="When the job was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="When the job was last updated"
    )

    # Results storage
    results = models.JSONField(
        default=dict,
        help_text="Job results: {repo_id: {'url': '...'} or {'error': '...'}}",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "PR Job"
        verbose_name_plural = "PR Jobs"

    def __str__(self):
        return f"PR Job {self.id} by {self.user.username}: {self.pr_title}"
