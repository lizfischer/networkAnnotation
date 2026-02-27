from django.contrib import admin
from .models import Document, Page


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["title", "project", "created_at"]
    list_filter = ["project"]


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ["__str__", "document", "order"]
    list_filter = ["document"]
