from __future__ import annotations

from django.db import models

from common.configs.constants.type_enums import TypeScopeChoices
from common.models.common_base_models import HatchUpBaseModel


class Type(HatchUpBaseModel):
    """Categorization type with a scope (document or form)."""

    title = models.CharField(max_length=255)
    scope = models.CharField(
        max_length=32,
        choices=TypeScopeChoices.choices,
    )

    class Meta:
        db_table = "common_type"
        verbose_name = "Type"
        verbose_name_plural = "Types"
        ordering = ["scope", "title"]
        indexes = [
            models.Index(fields=["scope"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.get_scope_display()})"
