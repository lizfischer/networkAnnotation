from django.urls import path

from . import views
from .views import (
    ProjectListView,
    ProjectCreateView,
    ProjectDetailView,
    ProjectDeleteView,
    project_list_partial,
    ProjectUpdateView,
)

app_name = "projects"
urlpatterns = [
    path("", ProjectListView.as_view(), name="list"),
    path("partial/", project_list_partial, name="project_list_partial"),
    # Project CRUD
    path("create/", ProjectCreateView.as_view(), name="create"),
    path("<str:pk>/", ProjectDetailView.as_view(), name="detail"),
    path(
        "<str:pk>/details-partial/",
        views.project_details_partial,
        name="details_partial",
    ),
    path("<str:pk>/edit", ProjectUpdateView.as_view(), name="edit"),
    path("<str:pk>/delete", ProjectDeleteView.as_view(), name="delete"),
    # EntityType CRUD (inline via HTMX)
    path("<str:pk>/entitytypes/add/", views.add_entitytype, name="add_entitytype"),
    path("entitytypes/<str:pk>/row/", views.entity_row_partial, name="entity_row"),
    path("entitytypes/<str:pk>/edit/", views.edit_entitytype, name="edit_entitytype"),
    path(
        "entitytypes/<str:pk>/delete/",
        views.delete_entitytype,
        name="delete_entitytype",
    ),
]
