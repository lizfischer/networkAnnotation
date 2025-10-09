# tests/test_text_field.py
import pytest
from django.core.exceptions import ValidationError

from apps.projects.schema_definitions.text import TextField


@pytest.fixture
def text_field():
    return TextField()


def test_clean_definition_valid(text_field):
    field_def = {
        "name": "title",
        "label": "Title",
        "type": "text",
        "required": True,
    }
    cleaned = text_field.clean_definition(field_def)
    assert cleaned["name"] == "title"


def test_clean_definition_missing_name(text_field):
    field_def = {"label": "Title", "type": "text"}
    with pytest.raises(ValidationError):
        text_field.clean_definition(field_def)


def test_clean_definition_missing_type(text_field):
    field_def = {"label": "Title", "name": "title"}
    with pytest.raises(ValidationError):
        text_field.clean_definition(field_def)


def test_clean_definition_missing_label(text_field):
    field_def = {"type": "text", "name": "title"}
    with pytest.raises(ValidationError):
        text_field.clean_definition(field_def)


def test_validate_valid_value(text_field):
    field_def = {"name": "title", "label": "Title", "type": "text"}
    # Valid short string
    text_field.validate("Hello", field_def)


def test_validate_invalid_value(text_field):
    field_def = {"name": "title", "label": "Title", "type": "text"}
    # Valid short string
    with pytest.raises(ValidationError):
        text_field.validate(2, field_def)


def test_validate_invalid_type(text_field):
    field_def = {"name": "title", "label": "Title", "type": "text"}
    with pytest.raises(ValidationError):
        text_field.validate(123, field_def)


def test_serialize_deserialize(text_field):
    value = "Hello World"
    serialized = text_field.serialize(value)
    deserialized = text_field.deserialize(serialized)
    assert deserialized == value
