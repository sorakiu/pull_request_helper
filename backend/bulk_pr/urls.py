from django.urls import path
from . import views

urlpatterns = [
    path("csrf/", views.CSRFTokenView.as_view(), name="csrf-token"),
    path("repos/", views.RepoListView.as_view(), name="repo-list"),
    path("jobs/", views.JobCreateView.as_view(), name="job-create"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
]
