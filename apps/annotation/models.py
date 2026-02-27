from django.core.exceptions import ValidationError
from django.db import models
import uuid
from apps.library.models import Page


class Annotation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="annotations")
    entity = models.ForeignKey(
        "projects.Entity", on_delete=models.PROTECT, related_name="annotations"
    )
    start_offset = models.PositiveIntegerField()
    end_offset = models.PositiveIntegerField()
    annotated_text = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_offset"]

    def __str__(self):
        return f"{self.annotated_text} → {self.entity.display_name}"

    def clean(self):
        super().clean()
        if self.end_offset <= self.start_offset:
            raise ValidationError("end_offset must be greater than start_offset.")
        if self.page and self.annotated_text:
            expected = self.page.text[self.start_offset : self.end_offset]
            if expected != self.annotated_text:
                raise ValidationError(
                    f"annotated_text does not match text at given offsets. "
                    f"Expected '{expected}', got '{self.annotated_text}'."
                )
