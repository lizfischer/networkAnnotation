from django.urls import path, reverse
from . import views


app_name = "projects"
urlpatterns = [
    path("create-form/", views.project_create_form, name="project_create_form"),
    path("", views.IndexView.as_view(), name="index"),
    path("<str:pk>/", views.ProjectDetailView.as_view(), name="detail"),
    path(
        "<str:project>/type/<str:pk>",
        views.EntityTypeDetailView.as_view(),
        name="entity_type",
    ),
    path(
        "<str:project>/new_type", views.EntityTypeCreateView.as_view(), name="new_type"
    ),
]
