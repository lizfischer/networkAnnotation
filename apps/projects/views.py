from django.shortcuts import render
from django.views import generic
from django.urls import reverse
from django.http import JsonResponse

from projects.models import Project, EntityType, allowed_field_types


class IndexView(generic.ListView):
    template_name = "projects/index.html"
    context_object_name = "project_list"

    def get_queryset(self):
        """Get all a user's projects"""
        return Project.objects.filter(owner=self.request.user)


class ProjectDetailView(generic.DetailView):
    model = Project
    template_name = "projects/detail.html"

    def get_context_data(self, **kwargs):
        context = super(ProjectDetailView, self).get_context_data(**kwargs)
        context["entity_types"] = EntityType.objects.filter(project=self.get_object())
        return context


class EntityTypeDetailView(generic.DetailView):
    model = EntityType
    template_name = "projects/entity_type.html"

    def post(self, request, *args, **kwargs):
        # todo
        print("Posted!")


class EntityTypeCreateView(generic.CreateView):
    model = EntityType
    fields = ["name", "color"]

    def get_context_data(self, **kwargs):
        context = super(EntityTypeCreateView, self).get_context_data(**kwargs)
        context["field_types"] = allowed_field_types
        project_entity_types = EntityType.objects.filter(project=self.kwargs["project"])
        context["entity_types"] = {str(x.id): x.name for x in project_entity_types}
        print(context["entity_types"])
        return context

    def get_success_url(self):
        return reverse(
            "projects:entity_type",
            kwargs={"pk": self.object.pk, "project": self.kwargs["project"]},
        )

    def form_valid(self, form):
        form.instance.project = Project.objects.get(id=self.kwargs["project"])
        all_fields = self.request.POST
        # todo process schema
        return super(EntityTypeCreateView, self).form_valid(form)
