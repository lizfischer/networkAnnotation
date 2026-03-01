from django.urls import path
from . import views

app_name = "library"

urlpatterns = [
    # Document URLs
    path(
        "projects/<uuid:project_id>/documents/new/",
        views.document_create,
        name="document_create",
    ),
    path(
        "projects/<uuid:project_id>/documents/<uuid:document_id>/",
        views.document_detail,
        name="document_detail",
    ),
    path(
        "projects/<uuid:project_id>/documents/<uuid:document_id>/edit/",
        views.document_edit,
        name="document_edit",
    ),
    path(
        "projects/<uuid:project_id>/documents/<uuid:document_id>/delete/",
        views.document_delete,
        name="document_delete",
    ),
    # Page URLs
    path(
        "projects/<uuid:project_id>/documents/<uuid:document_id>/pages/new/",
        views.page_create,
        name="page_create",
    ),
    path(
        "projects/<uuid:project_id>/documents/<uuid:document_id>/pages/<uuid:page_id>/",
        views.page_detail,
        name="page_detail",
    ),
    path(
        "projects/<uuid:project_id>/documents/<uuid:document_id>/pages/<uuid:page_id>/edit/",
        views.page_edit,
        name="page_edit",
    ),
    path(
        "projects/<uuid:project_id>/documents/<uuid:document_id>/pages/<uuid:page_id>/delete/",
        views.page_delete,
        name="page_delete",
    ),
]
