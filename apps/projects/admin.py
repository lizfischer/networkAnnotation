from django.contrib import admin

from apps.projects.models import EntityType, Entity, Project
from apps.library.models import TextDocument

admin.site.register(EntityType)
admin.site.register(Entity)
admin.site.register(Project)
admin.site.register(TextDocument)
