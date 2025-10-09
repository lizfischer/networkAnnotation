import uuid

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


class EntityType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class Entity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
