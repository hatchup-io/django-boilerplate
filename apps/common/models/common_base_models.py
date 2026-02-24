from django.db import models

from apps.common.managers.common_base_managers import HatchUpBaseManager


class HatchUpBaseModel(models.Model):
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = HatchUpBaseManager()

    class Meta:
        abstract = True
        ordering = ["-created_at"]
