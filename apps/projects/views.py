import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    DetailView,
    DeleteView,
    CreateView,
    TemplateView,
    UpdateView,
)

from networkAnnotation.decorators import htmx_only
from .forms import ProjectForm, EntityTypeForm
from apps.projects.models import Project, EntityType
from .schema_definitions.registry import FIELD_REGISTRY

"""
Project List View
"""


class ProjectListView(LoginRequiredMixin, TemplateView):
    template_name = "project_list.html"


@login_required
@htmx_only
def project_list_partial(request):
    """Returns only the list HTML for htmx swaps. This makes the back button a better experience"""
    projects = Project.objects.filter(owner=request.user)
    return render(
        request, "partials/project_list_partial.html", {"project_list": projects}
    )


"""
Project CRUD
"""


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "project_create.html"

    def get_success_url(self):
        # Redirect to the detail page of the newly created object
        return reverse_lazy("projects:detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = "project_detail.html"

    def get_context_data(self, **kwargs):
        context = super(ProjectDetailView, self).get_context_data(**kwargs)
        entity_types = self.object.entity_types.all()
        context["entity_types"] = entity_types
        context["schemas"] = {
            et.id: et.schema_object for et in entity_types
        }  # optional: also pass deserialized schema
        context["breadcrumbs"] = [
            {
                "label": "My Projects",
                "link": reverse_lazy("projects:list"),
                "icon": None,
            },
            {"label": self.object.title, "link": None, "icon": None},
        ]
        return context


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    # fields = ["title", "description"]
    template_name = "partials/project_edit_partial.html"

    def get_success_url(self):
        # redirect back to the detail page after saving
        return reverse_lazy("projects:details_partial", kwargs={"pk": self.object.pk})


@login_required
@htmx_only
def project_details_partial(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(
        request, "partials/project_details_partial.html", {"project": project}
    )


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = "confirm_modal.html"
    success_url = reverse_lazy("projects:list")

    def get_context_data(self, **kwargs):
        context = super(ProjectDeleteView, self).get_context_data(**kwargs)
        return context | {
            "url": reverse_lazy("projects:delete", kwargs={"pk": self.object.pk}),
            "target": "body",
            "prompt": f"Are you sure you want to delete {self.object}?",
            "confirm_text": "Delete",
        }


"""
EntityType CRUD
"""


@login_required
@htmx_only
def add_entitytype(request, pk):
    project = get_object_or_404(Project, pk=pk)
    form = EntityTypeForm(request.POST or None, project=project)
    if request.method == "POST":
        if form.is_valid():
            entity = form.save(commit=False)
            entity.project = project
            entity.save()
            return render(
                request,
                "partials/entitytype_list_partial.html",
                {"entity": entity, "new": True},
            )
            # If not valid, re-render form with errors
        print("INVALID!")
        return render(
            request,
            "partials/entitytype_edit_partial.html",
            {
                "form": form,
                "project": project,
                "field_types": FIELD_REGISTRY.keys(),
            },
        )
    return render(
        request,
        "partials/entitytype_edit_partial.html",
        {
            "form": form,
            "project": project,
            "field_types": FIELD_REGISTRY.keys(),
        },
    )


@login_required
@htmx_only
def entity_row_partial(request, pk):
    entity = get_object_or_404(EntityType, pk=pk)
    return render(request, "partials/entitytype_list_partial.html", {"entity": entity})


@login_required
@htmx_only
def edit_entitytype(request, pk):
    entity = get_object_or_404(EntityType, pk=pk)
    form = EntityTypeForm(request.POST or None, instance=entity)
    project_entity_types = entity.project.entity_types.all()
    if request.method == "POST" and form.is_valid():
        form.save()
        entity = get_object_or_404(EntityType, pk=pk)
        schema = json.dumps(entity.schema)
        return render(
            request,
            "partials/entitytype_list_partial.html",
            {
                "entity": entity,
                "schema_json": schema,
                "entity_types": project_entity_types,
            },
        )

    schema = json.dumps(entity.schema)
    return render(
        request,
        "partials/entitytype_edit_partial.html",
        {
            "form": form,
            "entity": entity,
            "schema_json": schema,
            "field_types": FIELD_REGISTRY.keys(),
            "entity_types": project_entity_types,
        },
    )


@login_required
@htmx_only
def delete_entitytype(request, pk):
    entity = get_object_or_404(EntityType, pk=pk)
    if request.method == "POST":
        entity.delete()
        return HttpResponse("")  # HTMX
    return render(
        request,
        "confirm_modal.html",
        {
            "url": reverse_lazy("projects:delete_entitytype", kwargs={"pk": entity.pk}),
            "target": f"#entity-{entity.id}",
            "prompt": f"Are you sure you want to delete {entity.name}?",
            "confirm_text": "Delete",
        },
    )
