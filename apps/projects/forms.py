from colorfield.widgets import ColorWidget
from django.forms import Form, CharField, ModelForm, TextInput, Textarea
from colorfield.forms import ColorField
from django.forms.models import inlineformset_factory

from apps.projects.models import Project, EntityType
from networkAnnotation.forms import BaseStyledForm


class ProjectForm(BaseStyledForm):
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
                    "rows": 2,
                    "placeholder": "Describe your project (optional)",
                }
            ),
        }


class EntityTypeForm(BaseStyledForm):
    class Meta:
        model = EntityType
        fields = ["name", "color", "description", "schema", "is_active"]
        widgets = {
            "color": ColorWidget,
            "description": Textarea(
                attrs={
                    "class": "input",
                    "rows": 1,
                    "placeholder": "Describe this entity type (optional)",
                }
            ),
        }


EntityTypeFormSet = inlineformset_factory(
    Project,
    EntityType,
    form=EntityTypeForm,
    extra=1,
    can_delete=True,
)
