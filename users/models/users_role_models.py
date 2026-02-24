from django.db import models
from common.models.common_base_models import HatchUpBaseModel
from django.contrib.auth.models import Group


class UserRole(HatchUpBaseModel):
    user_id = models.ForeignKey("users.User", on_delete=models.CASCADE)
    role_id = models.ForeignKey(Group, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "User Role"
        verbose_name_plural = "User Roles"
        ordering = ["-created_at"]

    def __str__(self):
        return self.user_id.full_name
