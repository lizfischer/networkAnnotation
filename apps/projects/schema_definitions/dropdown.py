# dropdown.py
from .base import BaseSchemaField
from django.core.exceptions import ValidationError


"""
Date fields have:
    - Name
    - Label
    - Required
    - Allowed choices
    - Value
    
"""


class DropdownField(BaseSchemaField):
    type = "dropdown"

    def clean_definition(self, field_def):
        super().clean_definition(field_def)
        choices = field_def.get("choices")
        if not choices or not isinstance(choices, list):
            raise ValidationError(
                "Dropdown field must define a non-empty 'choices' list."
            )
        return field_def

    def validate(self, value, field_def):
        if value is None:
            return
        if value not in field_def.get("choices", []):
            raise ValidationError(
                f"{field_def['name']} must be one of {field_def['choices']}."
            )
