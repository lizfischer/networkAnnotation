from django.db.models.expressions import result
from django.core.exceptions import ValidationError
from apps.projects.schema_definitions.registry import get_field_class


def serialize_properties(schema, properties):
    """
    Convert properties (field values) into JSON
    :param schema:
    :param properties:
    :return:
    """
    result = {}
    for field_def in schema:
        name = field_def.get("name")
        field_type = field_def.get("type")
        field_class = get_field_class(field_type)
        value = properties.get(name)
        result[name] = field_class.serialize(value)
    return result


def deserialize_properties(schema, properties):
    result = {}
    for field_def in schema:
        name = field_def.get("name")
        field_type = field_def.get("field_type")
        field_class = get_field_class(field_type)
        value = properties.get(name)
        result[name] = field_class.deserialize(value)
    return result


def deserialize_schema(schema_json):
    """
    Convert schema JSON into Python field objects.
    Each field object has a .to_dict() method with all relevant attributes.
    """
    field_objects = []
    for field_def in schema_json:
        field_type = field_def.get("type")
        if not field_type:
            continue
        cls = get_field_class(field_type)
        obj = cls(**field_def)
        obj.clean_definition(field_def)
        field_objects.append(obj)
    return field_objects


def validate_metadata(schema, metadata):
    """
    Validate a metadata dict against a schema (list of field defs).
    Raises ValidationError if any field fails.
    Written by Claude
    """
    errors = {}
    field_names = {f["name"] for f in schema}

    # Check display_name is present
    if "display_name" not in field_names:
        raise ValidationError("Schema must include a 'display_name' field.")
    if not metadata.get("display_name"):
        raise ValidationError("'display_name' is required.")

    for field_def in schema:
        name = field_def["name"]
        value = metadata.get(name)

        # Check required fields
        if field_def.get("required") and value is None:
            errors[name] = f"'{name}' is required."
            continue

        # Run field-level validation
        try:
            field_cls = get_field_class(field_def["type"])
            field_obj = field_cls(**field_def)
            field_obj.validate(value, field_def)
        except ValidationError as e:
            errors[name] = str(e)

    if errors:
        raise ValidationError(errors)
