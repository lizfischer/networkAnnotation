from django.core.exceptions import ValidationError
from django.test import TestCase

from projects.models import EntityType


class EntityTypeSchemaModelTests(TestCase):

    def test_malformed_schema(self):
        with self.assertRaises(ValidationError):
            EntityType(name="foo", schema={"test"}).save()

    def test_bad_field_names(self):
        with self.assertRaises(ValidationError):
            EntityType(name="foo", schema={"": "text"}).save()
        with self.assertRaises(ValidationError):
            EntityType(name="foo", schema={123: "text"}).save()

    def test_missing_type(self):
        with self.assertRaises(ValidationError):
            EntityType(name="foo", schema={"name": "date"}).save()

        with self.assertRaises(ValidationError):
            EntityType(name="foo", schema={"name": {}}).save()

    def test_allowed_field_types(self):
        # Test valid types
        try:
            x = EntityType(name="foo", schema={"name": {"type": "text"}})
            x.save()

            EntityType(name="foo", schema={"name": {"type": "number"}}).save()
            EntityType(name="foo", schema={"name": {"type": "date"}}).save()
            EntityType(name="foo", schema={"name": {"type": "geo"}}).save()
            EntityType(
                name="foo", schema={"name": {"type": "list", "options": ["cat", "dog"]}}
            ).save()
            EntityType(name="foo", schema={"name": {"type": "bool"}}).save()
            EntityType(
                name="foo", schema={"name": {"type": "entity", "options": str(x.id)}}
            ).save()

        except Exception as e:
            self.fail(e)

    def test_disallowed_field_types(self):
        # Test invalid types
        with self.assertRaises(ValidationError):
            EntityType(name="foo", schema={"name": {"type": ""}}).save()
        with self.assertRaises(ValidationError):
            EntityType(name="foo", schema={"name": {"type": "ewteaet"}}).save()
        with self.assertRaises(ValidationError):
            EntityType(name="foo", schema={"name": {"type": 1234}}).save()
        with self.assertRaises(ValidationError):
            EntityType(name="foo", schema={"name": {"type": ["text"]}}).save()

    def test_missing_list_options(self):
        with self.assertRaises(ValidationError):
            EntityType(name="foo", schema={"name": {"type": "list"}}).save()

        with self.assertRaises(ValidationError):
            EntityType(
                name="foo", schema={"name": {"type": "list", "options": None}}
            ).save()

    def test_bad_entity_field(self):
        with self.assertRaises(ValidationError):
            EntityType(name="foo", schema={"name": {"type": "entity"}}).save()

        with self.assertRaises(ValidationError):
            EntityType(
                name="foo", schema={"name": {"type": "entity", "options": None}}
            ).save()
        with self.assertRaises(ValidationError):
            EntityType(
                name="foo", schema={"name": {"type": "entity", "options": [123]}}
            ).save()

        with self.assertRaises(ValidationError):
            EntityType(
                name="foo", schema={"name": {"type": "entity", "options": "cats"}}
            ).save()
