# latlong.py
from .base import BaseSchemaField
from django.core.exceptions import ValidationError


class LatLongField(BaseSchemaField):
    type = "latlong"

    def validate(self, value, field_def):
        if value is None:
            return
        if not (isinstance(value, dict) and "lat" in value and "long" in value):
            raise ValidationError(
                f"{field_def['name']} must be a dict with 'lat' and 'long'."
            )
        lat = value["lat"]
        long = value["long"]
        if not isinstance(lat, (int, float)) or not isinstance(long, (int, float)):
            raise ValidationError(f"{field_def['name']} lat/long must be numeric.")
        if not (-90 <= lat <= 90):
            raise ValidationError(
                f"{field_def['name']} latitude must be between -90 and 90."
            )
        if not (-180 <= long <= 180):
            raise ValidationError(
                f"{field_def['name']} longitude must be between -180 and 180."
            )
