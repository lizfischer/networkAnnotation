from django.contrib import admin
from .models import Annotation


@admin.register(Annotation)
class AnnotationAdmin(admin.ModelAdmin):
    list_display = ["annotated_text", "entity", "page", "start_offset", "end_offset"]
    list_filter = ["entity__entity_type", "page__document"]
