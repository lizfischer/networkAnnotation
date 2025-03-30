from django.contrib import admin

from .models import EntityType, Entity

admin.site.register(EntityType)
admin.site.register(Entity)
