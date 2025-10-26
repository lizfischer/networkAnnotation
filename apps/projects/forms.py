import json

from django.forms import TextInput, Textarea, HiddenInput, ValidationError
from colorfield.widgets import ColorWidget
from apps.projects.models import Project, EntityType
from django.forms import ModelForm


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ["title", "description"]
        widgets = {
            "title": TextInput(
                attrs={
                    "class": "input input-bordered w-full",
                }
            ),
            "description": Textarea(
                attrs={
                    "class": "textarea",
                    "rows": 2,
                }
            ),
        }


class EntityTypeForm(ModelForm):
    class Meta:
        model = EntityType
        fields = ["name", "color", "description", "is_active", "schema"]
        # help_texts = {
        #     "description": "Describe this entity type (optional)",
        # }
        widgets = {
            "schema": HiddenInput(),
            "color": ColorWidget,
            "description": Textarea(
                attrs={"class": "input", "rows": 1},
            ),
        }

    def clean_schema(self):
        value = self.cleaned_data.get("schema")
        print(value)
        # if the hidden field came through as a string, parse it
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                raise ValidationError("Invalid JSON in schema")

            if not isinstance(parsed, list):
                raise ValidationError("Schema must be a list of field definitions")

            return parsed
        return value
