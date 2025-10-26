from django import template

BASE_INPUT_CLASS = " w-full focus-within:outline-hidden"
register = template.Library()


@register.inclusion_tag("form_parts/field_generic.html")
def render_field(field):
    widget = field.field.widget.__class__.__name__.lower()
    if "checkbox" in widget:
        template_name = "form_parts/field_checkbox.html"
    elif "textarea" in widget:
        template_name = "form_parts/field_textarea.html"
    else:
        template_name = "form_parts/field_text.html"
    return {"field": field, "template_name": template_name}


@register.filter
def add_classes(field, css_classes):
    return field.as_widget(attrs={"class": css_classes})


@register.filter
def add_placeholder(field, placeholder):
    return field.as_widget(attrs={"placeholder": placeholder})


@register.filter
def add_attrs(field, arg_string=""):
    """
    Add multiple HTML attributes to a form field.
    Usage:
        {{ field|add_attrs:"class:input input-bordered,placeholder:Custom text" }}

    If no placeholder is provided, it defaults to a space (for floating label)
    """
    # Parse comma-separated key:value pairs
    attrs = {}
    if arg_string:
        for pair in arg_string.split(","):
            if ":" in pair:
                key, val = pair.split(":", 1)
                attrs[key.strip()] = val.strip()

    # If no placeholder explicitly provided, use the field's label
    if "placeholder" not in attrs:
        attrs["placeholder"] = " "

    # Ensure base classes are always applied
    attrs["class"] += BASE_INPUT_CLASS

    # Merge with any existing attrs on the widget
    final_attrs = field.field.widget.attrs.copy()
    final_attrs.update(attrs)

    # Render the field with the new attributes
    return field.as_widget(attrs=final_attrs)
