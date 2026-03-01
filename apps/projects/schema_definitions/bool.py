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
        if value is None or value == "":
            return
        if isinstance(value, bool):
            return
        # Coerce string from JSON form input
        if isinstance(value, str) and value.lower() in (
            "true",
            "false",
            "1",
            "0",
            "yes",
            "no",
        ):
            return
        raise ValidationError(f"{field_def['name']} must be a boolean.")
