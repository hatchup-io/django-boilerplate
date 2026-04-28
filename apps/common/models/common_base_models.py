from django.db import models

from apps.common.managers.common_base_managers import HatchUpBaseManager


class HatchUpBaseModel(models.Model):
    """
    Soft-deletable, auditable base model.

    `objects` is the default manager and hides soft-deleted rows.
    `all_objects` returns every row (including soft-deleted) — use sparingly,
    typically only in admin actions, data migrations, or audit jobs.
    """

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = HatchUpBaseManager()
    all_objects = models.Manager()  # noqa: DJ012  audit manager — bypasses soft-delete filter

    class Meta:
        abstract = True
        ordering = ["-created_at"]
