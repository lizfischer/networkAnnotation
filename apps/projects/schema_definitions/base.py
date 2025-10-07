from django.core.exceptions import ValidationError


class BaseSchemaField:
    type = None

    def validate(self, value, field_def):
        raise NotImplementedError()

    def serialize(self, value):
        return value

    def deserialize(self, value):
        return value

    def clean_definition(self, field_def):
        """
        Validate the *schema definition* of a field (not its value).
        Ensures structural correctness.
        """
        # Required core keys
        required_keys = ["name", "label", "type"]
        for key in required_keys:
            if key not in field_def:
                raise ValidationError(f"Missing '{key}' in field definition.")

        # Ensure type matches class
        if field_def["type"] != self.type:
            raise ValidationError(
                f"Field definition type '{field_def['type']}' "
                f"does not match registered field '{self.type}'."
            )

        # Quick sanity checks
        if not isinstance(field_def["name"], str):
            raise ValidationError("Field 'name' must be a string.")
        if not isinstance(field_def["label"], str):
            raise ValidationError("Field 'label' must be a string.")
        if "required" in field_def and not isinstance(field_def["required"], bool):
            raise ValidationError("'required' must be a boolean if provided.")

        return field_def
