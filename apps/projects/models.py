import uuid

from django.db import models
from django.contrib.auth.models import User
from colorfield.fields import ColorField
from tailwind.validate import ValidationError

from apps.projects.schema_definitions.registry import get_field_class
from apps.projects.services.schema_service import deserialize_schema


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=100, default="My Project")
    description = models.TextField(blank=True, null=True)
    editors = models.ManyToManyField(User, related_name="editors", blank=True)
    viewers = models.ManyToManyField(User, related_name="viewers", blank=True)

    def __str__(self):
        return self.title


class EntityType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="entity_types"
    )
    name = models.CharField(max_length=100)
    color = ColorField(default="#f0dc48")
    description = models.TextField(blank=True)
    schema = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("project", "name")

    def __str__(self):
        return f"{self.name} ({self.project.title})"

    def clean(self):
        super().clean()
        if not isinstance(self.schema, list):
            raise ValidationError("Schema must be a list of field definitions")

        for field_def in self.schema:
            if "type" not in field_def:
                raise ValidationError(f"Field {field_def} must have a 'type' field")
            field_cls = get_field_class(field_def["type"])
            field_obj = field_cls(**field_def)
            field_obj.clean_definition(field_def)

    @property
    def schema_object(self):
        return deserialize_schema(self.schema)


class Entity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
