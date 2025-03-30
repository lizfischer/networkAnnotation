from django.core.exceptions import ValidationError
from django.db import models
from django.db.migrations.serializer import TypeSerializer

from projects.apps import ProjectsConfig


class EntityType(models.Model):
    # Allowed schema field types
    #     Free text
    #     Number
    #     Date
    #     Lat/Long
    #     Dropdown list of text options
    #     Bool (checkbox)
    #     Entity of type X
    #     todo: figure out what happens if an entity type is deleted

    id = models.UUIDField(primary_key=True)
    # project = models.ForeignKey(Project)
    name = models.CharField()
    schema = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # verify schema is ~ of format {'field name': 'type'}
        # and that all 'type's are in allowed list
        super().save(*args, **kwargs)

    @staticmethod
    def validate_filled_schema(metadata):
        # check that all field values are valid for their type
        pass


class Entity(models.Model):
    id = models.UUIDField(primary_key=True)
    type = models.ForeignKey(EntityType, on_delete=models.PROTECT)
    label = models.CharField(max_length=120, default="")
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.label} ({self.type})"

    def save(self, *args, **kwargs):
        self.type.validate_filled_schema(self.metadata)
        super().save(*args, **kwargs)
