from django.core.exceptions import ValidationError


class BaseSchemaField:
    type = None

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.label = kwargs.get("label")
        self.required = kwargs.get("required", False)
        # store the original definition so type-specific fields can access extras
        self._definition = kwargs

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

    def to_dict(self):
        """Return a dict suitable for templates or JSON serialization"""
        result = {
            "name": self.name,
            "label": self.label,
            "type": self.type,
            "required": self.required,
        }
        # Include any extra keys in the original definition (like max_length, options)
        extras = {k: v for k, v in self._definition.items() if k not in result}
        result.update(extras)
        return result
