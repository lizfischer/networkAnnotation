from django.contrib import admin

from .models import EntityType, Entity, Project, TextDocument

admin.site.register(EntityType)
admin.site.register(Entity)
admin.site.register(Project)
admin.site.register(TextDocument)
