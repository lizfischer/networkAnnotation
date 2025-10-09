from django.core.exceptions import ValidationError
from .base import BaseSchemaField


class TextField(BaseSchemaField):
    type = "text"

    def validate(self, value, field_def):
        if value is None:
            return
        if not isinstance(value, str):
            raise ValidationError(f"{field_def['name']} must be a string")

    def serialize(self, value):
        return value

    def deserialize(self, value):
        if value is None:
            return None
        return str(value)

    def clean_definition(self, field_def):
        super().clean_definition(field_def)
        return field_def

    # Todo: support max length?
