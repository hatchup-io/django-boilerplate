from collections.abc import Iterable

from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.auth.models import _auser_get_permissions
from django.contrib.auth.models import _auser_has_perm
from django.contrib.auth.models import _user_get_permissions
from django.contrib.auth.models import _user_has_module_perms
from django.contrib.auth.models import _user_has_perm
from django.db import models
from django.utils.translation import gettext_lazy as _


class PermissionsMixin(models.Model):
    """
    Add the fields and methods necessary to support the Group and Permission
    models using the ModelBackend.
    """

    is_superuser = models.BooleanField(
        _("superuser status"),
        default=False,
        help_text=_("Designates that this user has all permissions without explicitly assigning them."),
    )
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates that this user can access the admin site."),
    )
    roles = models.ManyToManyField(
        Group,
        through="users.UserRole",
        blank=True,
        related_name="user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("user permissions"),
        blank=True,
        help_text=_("Specific permissions for this user."),
        related_name="user_set",
        related_query_name="user",
    )

    class Meta:
        abstract = True

    def get_user_permissions(self, obj=None):
        return _user_get_permissions(self, obj, "user")

    async def aget_user_permissions(self, obj=None):
        return await _auser_get_permissions(self, obj, "user")

    def get_group_permissions(self, obj=None):
        return _user_get_permissions(self, obj, "group")

    async def aget_group_permissions(self, obj=None):
        return await _auser_get_permissions(self, obj, "group")

    def get_all_permissions(self, obj=None):
        return _user_get_permissions(self, obj, "all")

    async def aget_all_permissions(self, obj=None):
        return await _auser_get_permissions(self, obj, "all")

    def has_perm(self, perm, obj=None):
        if self.is_active and self.is_superuser:
            return True
        return _user_has_perm(self, perm, obj)

    async def ahas_perm(self, perm, obj=None):
        if self.is_active and self.is_superuser:
            return True
        return await _auser_has_perm(self, perm, obj)

    def has_perms(self, perm_list, obj=None):
        if not isinstance(perm_list, Iterable) or isinstance(perm_list, str):
            raise ValueError("perm_list must be an iterable of permissions.")
        return all(self.has_perm(perm, obj) for perm in perm_list)

    async def ahas_perms(self, perm_list, obj=None):
        if not isinstance(perm_list, Iterable) or isinstance(perm_list, str):
            raise ValueError("perm_list must be an iterable of permissions.")
        for perm in perm_list:
            if not await self.ahas_perm(perm, obj):
                return False
        return True

    def has_module_perms(self, app_label):
        if self.is_active and self.is_superuser:
            return True
        return _user_has_module_perms(self, app_label)

    async def ahas_module_perms(self, app_label):
        if self.is_active and self.is_superuser:
            return True
        return None
