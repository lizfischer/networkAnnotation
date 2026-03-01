from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from apps.projects.models import Project
from .models import Document, Page


# ---- DOCUMENT VIEWS ----


@login_required
def document_create(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        if not title:
            messages.error(request, "Title is required.")
        else:
            doc = Document.objects.create(
                project=project,
                title=title,
                description=description,
            )
            return redirect(
                "library:document_detail", project_id=project_id, document_id=doc.id
            )

    return render(
        request,
        "document_form.html",
        {
            "project": project,
            "breadcrumbs": [
                {"label": "Projects", "link": "/projects/"},
                {"label": project.title, "link": f"/projects/{project_id}/"},
                {"label": "New Document"},
            ],
        },
    )


@login_required
def document_detail(request, project_id, document_id):
    project = get_object_or_404(Project, pk=project_id)
    document = get_object_or_404(Document, pk=document_id, project=project)
    pages = document.pages.all()  # ordered by `order` via Meta

    return render(
        request,
        "document_detail.html",
        {
            "project": project,
            "document": document,
            "pages": pages,
            "breadcrumbs": [
                {"label": "Projects", "link": "/projects/"},
                {"label": project.title, "link": f"/projects/{project_id}/"},
                {"label": document.title},
            ],
        },
    )


@login_required
def document_edit(request, project_id, document_id):
    project = get_object_or_404(Project, pk=project_id)
    document = get_object_or_404(Document, pk=document_id, project=project)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        if not title:
            messages.error(request, "Title is required.")
        else:
            document.title = title
            document.description = description
            document.save()
            return redirect(
                "library:document_detail",
                project_id=project_id,
                document_id=document_id,
            )

    return render(
        request,
        "document_form.html",
        {
            "project": project,
            "document": document,
            "breadcrumbs": [
                {"label": "Projects", "link": "/projects/"},
                {"label": project.title, "link": f"/projects/{project_id}/"},
                {
                    "label": document.title,
                    "link": f"/projects/{project_id}/documents/{document_id}/",
                },
                {"label": "Edit"},
            ],
        },
    )


@login_required
def document_delete(request, project_id, document_id):
    project = get_object_or_404(Project, pk=project_id)
    document = get_object_or_404(Document, pk=document_id, project=project)

    if request.method == "POST":
        document.delete()
        return redirect("projects:detail", pk=project_id)

    return render(
        request,
        "document_confirm_delete.html",
        {
            "project": project,
            "document": document,
            "breadcrumbs": [
                {"label": "Projects", "link": "/projects/"},
                {"label": project.title, "link": f"/projects/{project_id}/"},
                {"label": document.title},
            ],
        },
    )


# ---- PAGE VIEWS ----


@login_required
def page_create(request, project_id, document_id):
    project = get_object_or_404(Project, pk=project_id)
    document = get_object_or_404(Document, pk=document_id, project=project)

    if request.method == "POST":
        files = request.FILES.getlist("files")
        if not files:
            messages.error(request, "Please upload at least one file.")
        else:
            # Sort files alphabetically by name so order is predictable
            files = sorted(files, key=lambda f: f.name)

            # Find the current highest order value so we append correctly
            last_order = (
                document.pages.order_by("-order")
                .values_list("order", flat=True)
                .first()
                or 0
            )

            for i, file in enumerate(files):
                text = file.read().decode("utf-8")
                Page.objects.create(
                    document=document,
                    order=last_order + i + 1,
                    title=file.name,
                    text=text,
                )

            messages.success(request, f"{len(files)} page(s) uploaded successfully.")
            return redirect(
                "library:document_detail",
                project_id=project_id,
                document_id=document_id,
            )

    return render(
        request,
        "page_form.html",
        {
            "project": project,
            "document": document,
            "breadcrumbs": [
                {"label": "Projects", "link": "/projects/"},
                {"label": project.title, "link": f"/projects/{project_id}/"},
                {
                    "label": document.title,
                    "link": f"/projects/{project_id}/documents/{document_id}/",
                },
                {"label": "Upload Pages"},
            ],
        },
    )


@login_required
def page_detail(request, project_id, document_id, page_id):
    project = get_object_or_404(Project, pk=project_id)
    document = get_object_or_404(Document, pk=document_id, project=project)
    page = get_object_or_404(Page, pk=page_id, document=document)

    # Get prev/next pages for navigation
    pages = list(document.pages.values_list("id", flat=True))
    current_index = pages.index(page.id)
    prev_page_id = pages[current_index - 1] if current_index > 0 else None
    next_page_id = pages[current_index + 1] if current_index < len(pages) - 1 else None

    return render(
        request,
        "page_detail.html",
        {
            "project": project,
            "document": document,
            "page": page,
            "prev_page_id": prev_page_id,
            "next_page_id": next_page_id,
            "breadcrumbs": [
                {"label": "Projects", "link": "/projects/"},
                {"label": project.title, "link": f"/projects/{project_id}/"},
                {
                    "label": document.title,
                    "link": f"/projects/{project_id}/documents/{document_id}/",
                },
                {"label": page.title or f"Page {page.order}"},
            ],
        },
    )


@login_required
def page_edit(request, project_id, document_id, page_id):
    project = get_object_or_404(Project, pk=project_id)
    document = get_object_or_404(Document, pk=document_id, project=project)
    page = get_object_or_404(Page, pk=page_id, document=document)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        text = request.POST.get("text", "")
        page.title = title
        page.text = text
        page.save()
        return redirect(
            "library:page_detail",
            project_id=project_id,
            document_id=document_id,
            page_id=page_id,
        )

    return render(
        request,
        "page_form.html",
        {
            "project": project,
            "document": document,
            "page": page,
            "breadcrumbs": [
                {"label": "Projects", "link": "/projects/"},
                {"label": project.title, "link": f"/projects/{project_id}/"},
                {
                    "label": document.title,
                    "link": f"/projects/{project_id}/documents/{document_id}/",
                },
                {
                    "label": page.title or f"Page {page.order}",
                    "link": f"/projects/{project_id}/documents/{document_id}/pages/{page_id}/",
                },
                {"label": "Edit"},
            ],
        },
    )


@login_required
def page_delete(request, project_id, document_id, page_id):
    project = get_object_or_404(Project, pk=project_id)
    document = get_object_or_404(Document, pk=document_id, project=project)
    page = get_object_or_404(Page, pk=page_id, document=document)

    if request.method == "POST":
        page.delete()
        return redirect(
            "library:document_detail", project_id=project_id, document_id=document_id
        )

    return render(
        request,
        "document_confirm_delete.html",
        {
            "project": project,
            "document": document,
            "page": page,
            "breadcrumbs": [
                {"label": "Projects", "link": "/projects/"},
                {"label": project.title, "link": f"/projects/{project_id}/"},
                {
                    "label": document.title,
                    "link": f"/projects/{project_id}/documents/{document_id}/",
                },
                {"label": page.title or f"Page {page.order}"},
            ],
        },
    )
