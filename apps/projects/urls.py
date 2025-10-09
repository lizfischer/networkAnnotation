from django.urls import path, reverse
from .views import (
    ProjectListView,
    ProjectCreateView,
    ProjectDetailView,
    ProjectDeleteView,
    project_list_partial,
)

app_name = "projects"
urlpatterns = [
    path("", ProjectListView.as_view(), name="list"),
    path("partial/", project_list_partial, name="project_list_partial"),
    path("create/", ProjectCreateView.as_view(), name="create"),
    path("<str:pk>/", ProjectDetailView.as_view(), name="detail"),
    path("<str:pk>/delete", ProjectDeleteView.as_view(), name="delete"),
]
