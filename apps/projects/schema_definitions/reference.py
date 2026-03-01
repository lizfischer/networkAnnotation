# reference.py
from .base import BaseSchemaField
from django.core.exceptions import ValidationError
from django.apps import apps

# todo: figure out what happens if an entity type is deleted

"""
Reference fields have:
    - Name
    - Label
    - Required
    - Type referenced
    - Value

"""


class ReferenceField(BaseSchemaField):
    type = "reference"

    def clean_definition(self, field_def):
        super().clean_definition(field_def)
        target_id = field_def.get("target_entity_type_id")
        if target_id is None:
            raise ValidationError(
                "Reference field must define 'target_entity_type_id'."
            )
        # Optional: verify that the target EntityType exists
        EntityType = apps.get_model("projects", "EntityType")
        if not EntityType.objects.filter(id=target_id).exists():
            raise ValidationError(
                f"Target EntityType with id {target_id} does not exist."
            )
        return field_def

    def validate(self, value, field_def):
        if value is None:
            return
        # Accept UUID strings (from JSON) or UUID objects
        import uuid

        try:
            value_uuid = uuid.UUID(str(value))
        except (ValueError, AttributeError):
            raise ValidationError(f"{field_def['name']} must be a valid entity UUID.")

        target_id = field_def.get("target_entity_type_id")
        Entity = apps.get_model("projects", "Entity")

        if (
            target_id
            and not Entity.objects.filter(
                id=value_uuid, entity_type_id=target_id
            ).exists()
        ):
            raise ValidationError(
                f"{field_def['name']} must reference a valid entity of the correct type."
            )
