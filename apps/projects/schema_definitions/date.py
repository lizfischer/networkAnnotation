# date.py
from .base import BaseSchemaField
from django.core.exceptions import ValidationError
from datetime import datetime


class DateField(BaseSchemaField):
    type = "date"

    def validate(self, value, field_def):
        if value is None:
            return

        # Plain string -- stored when date couldn't be parsed by the JS widget
        if isinstance(value, str):
            return

        # Structured date object: {"iso": "...", "precision": "...", "original": "..."}
        if isinstance(value, dict):
            iso = value.get("iso")
            precision = value.get("precision")
            original = value.get("original")

            if not iso:
                raise ValidationError(
                    f"{field_def['name']}: structured date must include 'iso'."
                )

            valid_precisions = {
                "day",
                "month",
                "year",
                "decade",
                "quarter_century",
                "century",
            }
            if precision not in valid_precisions:
                raise ValidationError(
                    f"{field_def['name']}: invalid precision '{precision}'. "
                    f"Must be one of {sorted(valid_precisions)}."
                )

            # Allow year 0000 (used for dates with no year, e.g. "April 30")
            if iso.startswith("0000-"):
                rest = iso[5:]  # "MM-DD"
                try:
                    datetime.strptime(rest, "%m-%d")
                except ValueError:
                    raise ValidationError(
                        f"{field_def['name']}: 'iso' is not a valid date, got '{iso}'."
                    )
                return

            try:
                datetime.fromisoformat(iso)
            except ValueError:
                raise ValidationError(
                    f"{field_def['name']}: 'iso' must be a valid ISO date string, got '{iso}'."
                )

            return

        raise ValidationError(
            f"{field_def['name']}: date value must be a string or structured date object."
        )
