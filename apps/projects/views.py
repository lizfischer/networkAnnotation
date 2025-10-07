from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import ListView, View, DetailView
from .forms import ProjectForm
from apps.projects.models import Project
from django.shortcuts import redirect


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = "project_list.html"
    context_object_name = "project_list"
    form = ProjectForm()

    def get_queryset(self):
        """Get all a user's projects"""
        return Project.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = ProjectForm()
        return context


class ProjectCreateView(LoginRequiredMixin, View):
    def post(self, request):
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            return redirect("projects:detail", pk=project.pk)
        # if invalid, re-render the list with errors
        projects = Project.objects.filter(owner=request.user)
        return render(
            request, "project_list.html", {"form": form, "projects": projects}
        )


class ProjectDetailView(DetailView):
    model = Project
    template_name = "detail.html"

    def get_context_data(self, **kwargs):
        context = super(ProjectDetailView, self).get_context_data(**kwargs)
        return context
