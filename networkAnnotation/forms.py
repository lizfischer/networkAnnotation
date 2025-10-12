from django.forms import ModelForm
from django.forms.widgets import Textarea, TextInput, CheckboxInput


class BaseStyledForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            widget.attrs.setdefault("class", "")
            input_type = getattr(widget, "input_type", None)

            if input_type in ["text", "email", "url", "color", "number"]:
                widget.attrs[
                    "class"
                ] += " input input-bordered w-full focus-within:outline-hidden"
            elif isinstance(widget, Textarea):
                widget.attrs[
                    "class"
                ] += " textarea textarea-bordered w-full focus-within:outline-hidden rounded-md"
            elif isinstance(widget, CheckboxInput):
                widget.attrs["class"] += " checkbox"
