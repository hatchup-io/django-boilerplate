from django.contrib.auth.models import Group
from django.db import models

from apps.common.models.common_base_models import HatchUpBaseModel


class UserRole(HatchUpBaseModel):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    role = models.ForeignKey(Group, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "User Role"
        verbose_name_plural = "User Roles"
        ordering = ["-created_at"]

    def __str__(self):
        return self.user.full_name
