from django.contrib import admin

from apps.projects.models import Project
from apps.library.models import TextDocument

admin.site.register(Project)
admin.site.register(TextDocument)
