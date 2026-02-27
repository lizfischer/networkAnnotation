from django.contrib import admin

from apps.projects.models import Project, EntityType, Entity

admin.site.register(Project)
admin.site.register(EntityType)
admin.site.register(Entity)
