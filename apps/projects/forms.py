from django.forms import Form, CharField, ModelForm, TextInput, Textarea
from colorfield.forms import ColorField

from apps.projects.models import Project


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ["title", "description"]
        widgets = {
            "title": TextInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "Project Name",
                }
            ),
            "description": Textarea(
                attrs={
                    "class": "textarea",
                    "rows": 3,
                    "placeholder": "Describe your project (optional)",
                }
            ),
        }
