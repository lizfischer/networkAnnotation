from django.forms import Form, CharField
from colorfield.forms import ColorField


class EntityTypeForm(Form):
    name = CharField(label="Name", max_length=100)
    color = ColorField(initial="#ffeb7a", format="hex")
