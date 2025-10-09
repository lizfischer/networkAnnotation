from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import (
    ListView,
    View,
    DetailView,
    DeleteView,
    CreateView,
    TemplateView,
)

from networkAnnotation.decorators import htmx_only
from .forms import ProjectForm
from apps.projects.models import Project
from django.shortcuts import redirect


# @method_decorator(never_cache, name="dispatch")
# class ProjectListView(LoginRequiredMixin, ListView):
#     model = Project
#     template_name = "project_list.html"
#     context_object_name = "project_list"
#     form = ProjectForm()
#
#     def get_queryset(self):
#         """Get all a user's projects"""
#         return Project.objects.filter(owner=self.request.user)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["form"] = ProjectForm()
#         return context


class ProjectListView(LoginRequiredMixin, TemplateView):
    template_name = "project_list.html"


@login_required
@htmx_only
def project_list_partial(request):
    """Returns only the list HTML for htmx swaps. This makes the back button a better experience"""
    projects = Project.objects.filter(owner=request.user)
    return render(request, "project_list_partial.html", {"project_list": projects})


class ProjectCreateView(CreateView):
    model = Project
    # fields = ["title", "description"]
    form_class = ProjectForm
    template_name = "project_create.html"

    def get_success_url(self):
        # Redirect to the detail page of the newly created object
        return reverse_lazy("projects:detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ProjectDeleteView(DeleteView):
    model = Project
    template_name = "project_confirm_delete.html"
    success_url = reverse_lazy("projects:list")


class ProjectDetailView(DetailView):
    model = Project
    template_name = "project_detail.html"

    def get_context_data(self, **kwargs):
        context = super(ProjectDetailView, self).get_context_data(**kwargs)
        return context
