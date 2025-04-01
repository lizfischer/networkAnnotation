from django.urls import path, reverse
from . import views


app_name = "projects"
urlpatterns = [
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
