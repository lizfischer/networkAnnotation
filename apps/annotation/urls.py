from django.urls import path
from . import api

app_name = "annotation"

urlpatterns = [
    path(
        "api/projects/<uuid:project_id>/entity-types/",
        api.entity_types,
        name="entity_types",
    ),
    path(
        "api/projects/<uuid:project_id>/entities/",
        api.entity_search,
        name="entity_search",
    ),
    path("api/pages/<uuid:page_id>/annotations/", api.annotations, name="annotations"),
    path(
        "api/pages/<uuid:page_id>/annotations/bulk-update/",
        api.annotations_bulk_update,
        name="annotations_bulk_update",
    ),
    path(
        "api/annotations/<uuid:annotation_id>/",
        api.annotation_detail,
        name="annotation_detail",
    ),
    path("api/pages/<uuid:page_id>/text/", api.page_text, name="page_text"),
    path(
        "api/projects/<uuid:project_id>/entities/create/",
        api.entity_create,
        name="entity_create",
    ),
    path(
        "api/entities/<uuid:entity_id>/",
        api.entity_update,
        name="entity_update",
    ),
]
