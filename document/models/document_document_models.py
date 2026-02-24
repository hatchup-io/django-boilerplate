from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models

from common.models.common_base_models import HatchUpBaseModel
from common.models.common_type_models import Type


class Document(HatchUpBaseModel):
    """Uploaded document; owned by user, optional type."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
    )
    type = models.ForeignKey(
        Type,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
    )
    filename = models.CharField(max_length=255)
    original_filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=20)
    file_path = models.CharField(max_length=500)
    file_size_bytes = models.IntegerField()
    content_hash = models.CharField(max_length=64, blank=True)

    class Meta:
        db_table = "document_document"
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user"]),
        ]

    def __str__(self) -> str:
        return self.original_filename or self.filename

    @property
    def file_url(self) -> str:
        return f"{settings.MEDIA_URL}{self.file_path}"
