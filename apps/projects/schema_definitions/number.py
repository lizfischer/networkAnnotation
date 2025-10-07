from django.core.exceptions import ValidationError
from .base import BaseSchemaField


class NumberField(BaseSchemaField):
    type = "text"

    def validate(self, value, field_def):
        if value is None:
            return
        if not isinstance(value, (float, int)):
            raise ValidationError(f"{field_def['name']} must be a number")

    def clean_definition(self, field_def):
        super().clean_definition(field_def)
        return field_def

    # Todo: support min and max values?
