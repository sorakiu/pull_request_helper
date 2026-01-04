from django.urls import path
from . import views

urlpatterns = [
    path("repos/", views.RepoListView.as_view(), name="repo-list"),
    path("jobs/", views.JobCreateView.as_view(), name="job-create"),
]
