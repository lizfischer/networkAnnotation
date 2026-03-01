"""
apps/annotation/api.py

JSON API endpoints consumed by the annotation canvas JS component.
All endpoints require login and return JSON.
"""

import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

from apps.library.models import Page
from apps.projects.models import Project, EntityType, Entity
from .models import Annotation


def json_error(message, status=400):
    """Helper to return a consistent error response."""
    return JsonResponse({"error": message}, status=status)


def json_unauthorized():
    return json_error("Unauthorized", status=401)


# ---- ENTITY TYPES ----


@login_required
@require_http_methods(["GET"])
def entity_types(request, project_id):
    """
    Return all active entity types for a project.
    Used to populate the entity type picker toolbar in the canvas.
    """
    project = get_object_or_404(Project, pk=project_id)

    types = project.entity_types.filter(is_active=True).values(
        "id", "name", "color", "schema"
    )
    return JsonResponse({"entity_types": list(types)})


# ---- ENTITY SEARCH ----


@login_required
@require_http_methods(["GET"])
def entity_search(request, project_id):
    """
    Type-ahead search of entities within a project.

    Query params:
        q        -- search string (matched against display_name in metadata)
        type_id  -- (optional) filter by entity type UUID
    """
    project = get_object_or_404(Project, pk=project_id)

    q = request.GET.get("q", "").strip()
    type_id = request.GET.get("type_id")

    if not q:
        return JsonResponse({"entities": []})

    # Filter by project, then optionally by type
    qs = Entity.objects.filter(project=project)
    if type_id:
        qs = qs.filter(entity_type_id=type_id)

    # Search against display_name in the metadata JSON field
    # Uses PostgreSQL JSON containment -- works for exact prefix matches
    # For fuzzier matching this could be replaced with a trigram search later
    qs = qs.filter(metadata__display_name__icontains=q)[:20]  # limit to 20 results

    results = [
        {
            "id": str(entity.id),
            "display_name": entity.display_name,
            "entity_type_id": str(entity.entity_type_id),
            "entity_type_name": entity.entity_type.name,
            "entity_type_color": entity.entity_type.color,
            "metadata": entity.metadata,
        }
        for entity in qs
    ]

    return JsonResponse({"entities": results})


# ---- ANNOTATIONS ----


@login_required
@require_http_methods(["GET", "POST"])
def annotations(request, page_id):
    """
    GET  -- return all annotations for a page (used on canvas load)
    POST -- create a new annotation
    """
    page = get_object_or_404(Page, pk=page_id)

    if request.method == "GET":
        annotations = page.annotations.select_related(
            "entity", "entity__entity_type"
        ).all()

        results = [
            {
                "id": str(a.id),
                "start_offset": a.start_offset,
                "end_offset": a.end_offset,
                "annotated_text": a.annotated_text,
                "entity_id": str(a.entity_id),
                "entity_display_name": a.entity.display_name,
                "entity_type_id": str(a.entity.entity_type_id),
                "entity_type_name": a.entity.entity_type.name,
                "entity_type_color": a.entity.entity_type.color,
            }
            for a in annotations
        ]

        return JsonResponse({"annotations": results})

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return json_error("Invalid JSON")

        entity_id = data.get("entity_id")
        start_offset = data.get("start_offset")
        end_offset = data.get("end_offset")

        # Validate required fields
        if not all([entity_id, start_offset is not None, end_offset is not None]):
            return json_error("entity_id, start_offset, and end_offset are required.")

        entity = get_object_or_404(Entity, pk=entity_id)

        # Snapshot the annotated text from the page
        annotated_text = page.text[start_offset:end_offset]
        if not annotated_text:
            return json_error("No text found at the given offsets.")

        annotation = Annotation(
            page=page,
            entity=entity,
            start_offset=start_offset,
            end_offset=end_offset,
            annotated_text=annotated_text,
        )

        try:
            annotation.full_clean()
        except Exception as e:
            return json_error(str(e))

        annotation.save()

        return JsonResponse(
            {
                "id": str(annotation.id),
                "start_offset": annotation.start_offset,
                "end_offset": annotation.end_offset,
                "annotated_text": annotation.annotated_text,
                "entity_id": str(annotation.entity_id),
                "entity_display_name": annotation.entity.display_name,
                "entity_type_id": str(annotation.entity.entity_type_id),
                "entity_type_name": annotation.entity.entity_type.name,
                "entity_type_color": annotation.entity.entity_type.color,
            },
            status=201,
        )


@login_required
@require_http_methods(["DELETE"])
def annotation_detail(request, annotation_id):
    """
    DELETE -- remove an annotation.
    Does not delete the underlying entity, just the span.
    """
    annotation = get_object_or_404(Annotation, pk=annotation_id)
    annotation.delete()
    return JsonResponse({"deleted": True})


# ---- PAGE TEXT ----


@login_required
@require_http_methods(["PUT"])
def page_text(request, page_id):
    """
    PUT -- save edited page text after edit mode.

    Accepts: { "text": "..." }
    Returns: { "saved": true, "invalidated_annotations": [...] }

    Checks each existing annotation to see if its annotated_text still matches
    the text at those offsets. If not, the annotation is flagged as invalidated
    and returned to the client for the warning UI -- but NOT automatically deleted.
    The client decides what to do with them.
    """
    page = get_object_or_404(Page, pk=page_id)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return json_error("Invalid JSON")

    new_text = data.get("text")
    if new_text is None:
        return json_error("'text' is required.")

    # Check which annotations are invalidated by the new text
    invalidated = []
    for annotation in page.annotations.select_related(
        "entity", "entity__entity_type"
    ).all():
        text_at_offsets = new_text[annotation.start_offset : annotation.end_offset]
        if text_at_offsets != annotation.annotated_text:
            invalidated.append(
                {
                    "id": str(annotation.id),
                    "annotated_text": annotation.annotated_text,
                    "entity_display_name": annotation.entity.display_name,
                    "entity_type_name": annotation.entity.entity_type.name,
                }
            )

    # Save the new text regardless -- client has already been warned
    page.text = new_text
    page.save()

    return JsonResponse(
        {
            "saved": True,
            "invalidated_annotations": invalidated,
        }
    )


# ---- ENTITY CREATE ----


@login_required
@require_http_methods(["POST"])
def entity_create(request, project_id):
    """
    POST -- create a new entity instance.

    Accepts: { "entity_type_id": "...", "metadata": { "display_name": "...", ... } }
    Returns: the created entity
    """
    project = get_object_or_404(Project, pk=project_id)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return json_error("Invalid JSON")

    entity_type_id = data.get("entity_type_id")
    metadata = data.get("metadata", {})

    if not entity_type_id:
        return json_error("entity_type_id is required.")

    entity_type = get_object_or_404(EntityType, pk=entity_type_id, project=project)

    entity = Entity(
        entity_type=entity_type,
        project=project,
        metadata=metadata,
    )

    try:
        entity.full_clean()
    except Exception as e:
        return json_error(str(e))

    entity.save()

    return JsonResponse(
        {
            "id": str(entity.id),
            "display_name": entity.display_name,
            "entity_type_id": str(entity.entity_type_id),
            "entity_type_name": entity.entity_type.name,
            "entity_type_color": entity.entity_type.color,
            "metadata": entity.metadata,
        },
        status=201,
    )
