from django.contrib.auth.models import AbstractBaseUser
from django.db import models

from common.models.common_base_models import HatchUpBaseModel
from users.managers.users_base_managers import UserManager
from users.models.users_permission_models import PermissionsMixin


class User(AbstractBaseUser, PermissionsMixin, HatchUpBaseModel):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=32, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-created_at"]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
