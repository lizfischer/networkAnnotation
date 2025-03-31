import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
import json
from projects.apps import ProjectsConfig


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=100, default="My Project")
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, blank=True, null=True
    )
    title = models.CharField(max_length=100, default="My Document")

    def __str__(self):
        return self.title

    class Meta:
        abstract = True


class TextDocument(Document):
    text = models.TextField(blank=True, null=True)


# Allowed schema field types
#     Free text
#     Number
#     Date
#     Lat/Long
#     Dropdown list of text options
#     Bool (checkbox)
#     Entity of type X
#     todo: figure out what happens if an entity type is deleted
allowed_field_types = ["text", "number", "date", "geo", "list", "bool", "entity"]


class FieldValueValidation:
    @staticmethod
    def validate(value, field_type, field_options):
        match field_type:
            case "text":
                return FieldValueValidation.text(value)
            case "number":
                return FieldValueValidation.number(value)
            case "date":
                return FieldValueValidation.date(value)
            case "geo":
                return FieldValueValidation.geo(value)
            case "list":
                return FieldValueValidation.list(value, field_options)
            case "bool":
                return FieldValueValidation.bool(value)
            case "entity":
                return FieldValueValidation.entity(value, field_options)

    @staticmethod
    def text(value):
        """
        Allows any string
        """
        if not isinstance(value, str):
            return ValidationError(
                "Text field value must be a string", code="invalid_text"
            )

    @staticmethod
    def number(value):
        """
        Allows float or int
        """
        if not isinstance(value, int) and not isinstance(value, float):
            return ValidationError(
                "Number field value must be an int or float", code="invalid_number"
            )

    @staticmethod
    def date(value):
        # todo: Implement date field validation
        pass

    @staticmethod
    def geo(value):
        valid = True
        if not isinstance(value, str):
            valid = False

        try:
            lat, long = value.split(",")
            lat = float(lat)
            long = float(long)

            if not (-90 <= lat <= 90) or not (-180 <= long <= 180):
                return ValidationError(
                    "Latitude must be between -90 and 90. Longitude must be between -180 and 180.",
                    code="geo_out_of_range",
                )

        except ValueError:
            valid = False

        if not valid:
            return ValidationError(
                "Geo field value must be decimal latitude & longitude separated by comma",
                code="invalid_geo",
            )

    @staticmethod
    def list(value, options):
        """
        Allows list of values specified in Options
        """
        if not isinstance(value, list) or not isinstance(options, list):
            return False
        for v in value:
            if v not in options:
                return False
        return True

    @staticmethod
    def bool(value):
        """
        Allows True/False
        """
        if not isinstance(value, bool):
            return ValidationError(
                "Bool field value must be a true/false", code="invalid_bool"
            )

    @staticmethod
    def entity(value, options):
        pass


class EntityType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, blank=True, null=True
    )
    name = models.CharField()
    schema = models.JSONField(default=dict, blank=True)

    def validate_schema(self):
        """
        Validate the EntityType's schema. Should be a dictionary with
        field names as keys, and dictionaries "type" and "options" as values.
        Each "type" must be in the allowed list, and the "options" must be
        valid for each "type"

        Raises ValidationError(s) if validation fails.
        """
        errors = []
        # Check schema is a dict
        if not isinstance(self.schema, dict):
            errors.append(ValidationError("Schema must be a dict"))
        else:
            # Check each field
            for field_name in self.schema:
                # Field name must be string with at least 1 character
                if not isinstance(field_name, str) or len(field_name) < 1:
                    errors.append(
                        ValidationError(
                            "Field name must be a string of at least 1 character.",
                            code="invalid_name",
                        )
                    )
                # Check type
                if (
                    not isinstance(self.schema[field_name], dict)
                    or "type" not in self.schema[field_name]
                ):
                    # If the field doesn't have a dict with it, or a "type" specified
                    errors.append(ValidationError("Type not specified", code="no_type"))
                else:
                    field_type = self.schema[field_name]["type"]
                    # Check for valid type
                    if field_type not in allowed_field_types:
                        errors.append(
                            ValidationError(
                                "Specified type not allowed", code="invalid_type"
                            )
                        )
                    # Check options for list
                    elif field_type == "list":
                        if "options" not in self.schema[field_name]:
                            errors.append(
                                ValidationError(
                                    "List fields must specify list options",
                                    code="missing_list_options",
                                )
                            )
                        elif not isinstance(
                            self.schema[field_name]["options"], list
                        ) or not all(
                            isinstance(x, str)
                            for x in self.schema[field_name]["options"]
                        ):
                            # If options is not a list of strings
                            errors.append(
                                ValidationError(
                                    "List fields must specify string list options",
                                    code="invalid_list_options",
                                )
                            )

                    # Check options for entity
                    elif field_type == "entity":
                        if "options" not in self.schema[field_name]:
                            errors.append(
                                ValidationError(
                                    "Entity fields must specify an EntityType ID in options",
                                    code="missing_entity_type",
                                )
                            )
                        else:
                            entity_type = self.schema[field_name]["options"]
                            if (
                                not isinstance(entity_type, str)
                                or not EntityType.objects.filter(
                                    id=entity_type
                                ).exists()
                            ):
                                errors.append(
                                    ValidationError(
                                        "EntityType not found.",
                                        code="invalid_entity_type",
                                    )
                                )
            if errors:
                raise ValidationError(errors)

    def validate_filled_schema(self, metadata):
        """
        For validating an Entity's use of this EntityType's schema.
        Raises ValidationError(s) on failed checks
        :param metadata: filled-in metadata schema
        """
        errors = []
        if not isinstance(metadata, dict):
            errors.append(ValidationError("Metadata must be a dict", code="malformed"))
        else:

            schema_fields = self.schema.keys()
            for field_name in metadata:
                if field_name not in schema_fields:
                    errors.append(
                        ValidationError(
                            "Field name not in schema", code="invalid_field"
                        )
                    )
                else:
                    # check that all field values are valid for their type
                    field_type = self.schema[field_name]["type"]
                    field_options = (
                        self.schema[field_name]["options"]
                        if "options" in self.schema[field_name]
                        else None
                    )
                    value = metadata[field_name]
                    error = FieldValueValidation.validate(
                        value, field_type, field_options
                    )
                    if error:
                        errors.append(error)
        if errors:
            raise ValidationError(errors)

    class Meta:
        unique_together = ["project", "name"]

    def __str__(self):
        return self.name

    def clean(self):
        self.validate_schema()
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Entity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.ForeignKey(EntityType, on_delete=models.PROTECT)
    label = models.CharField(max_length=120, default="")
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.label} ({self.type})"

    def clean(self):
        self.type.validate_filled_schema(self.metadata)
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
