# bool.py
from .base import BaseSchemaField
from django.core.exceptions import ValidationError

"""
Bool fields have:
    - Name
    - Label
    - Required
    - Value
"""


class BoolField(BaseSchemaField):
    type = "bool"

    def validate(self, value, field_def):
        if value is None:
            return
        if not isinstance(value, bool):
            raise ValidationError(f"{field_def['name']} must be a boolean.")
