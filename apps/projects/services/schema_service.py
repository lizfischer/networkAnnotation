from django.db.models.expressions import result

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
