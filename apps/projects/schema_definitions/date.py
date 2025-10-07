# date.py
from .base import BaseSchemaField
from django.core.exceptions import ValidationError
from datetime import datetime


class DateField(BaseSchemaField):
    type = "date"

    def validate(self, value, field_def):
        if value is None:
            return
        if not isinstance(value, str):
            raise ValidationError(
                f"{field_def['name']} must be a date string (ISO format)."
            )
        try:
            datetime.fromisoformat(value)
        except ValueError:
            raise ValidationError(
                f"{field_def['name']} must be a valid ISO date string."
            )
