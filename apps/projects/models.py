import uuid

from django.db import models
from django.contrib.auth.models import User
from colorfield.fields import ColorField

# from tailwind.validate import ValidationError
from django.core.exceptions import ValidationError
from apps.projects.schema_definitions.registry import get_field_class
from apps.projects.services.schema_service import deserialize_schema, validate_metadata


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

        # Ensure schema is a list
        if not isinstance(self.schema, list):
            raise ValidationError("Schema must be a list of field definitions")

        # Enforce display_name field exists
        field_names = [f.get("name") for f in self.schema]
        if "display_name" not in field_names:
            raise ValidationError("Schema must include a field named 'display_name'.")

        # Ensure each field in schema has a type ?
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
    """
    Written by Claude
    """

    class Meta:
        verbose_name_plural = "Entities"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_type = models.ForeignKey(
        EntityType, on_delete=models.PROTECT, related_name="entities"
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="entities"
    )
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name

    @property
    def display_name(self):
        return self.metadata.get("display_name", f"[unnamed {self.entity_type.name}]")

    def save(self, *args, **kwargs):
        # Denormalize project from entity_type
        self.project = self.entity_type.project
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        validate_metadata(self.entity_type.schema, self.metadata)
