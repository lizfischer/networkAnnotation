import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from colorfield.fields import ColorField


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=100, default="My Project")
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


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
