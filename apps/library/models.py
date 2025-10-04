from django.db import models
import uuid
from apps.projects.models import Project


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, blank=True, null=True
    )
    title = models.CharField(max_length=100, default="My Document")

    def __str__(self):
        return self.title

    class Meta:
        abstract = True


class TextDocument(Document):
    text = models.TextField(blank=True, null=True)
