from __future__ import annotations

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.common.models.common_base_models import HatchUpBaseModel


class UserObjectPermission(HatchUpBaseModel):
    """
    Internal object-level permission record (guardian replacement).

    Design:
    - One row means: `user` has `perm_codename` on (content_type, object_id).
    - `perm_codename` is a full permission string: "{app_label}.{codename}"
      e.g. "users.view_user"

    Performance:
    - LIST filtering uses a subquery against this table (single query, no N+1).
    - DETAIL permission checks can be cached per request in the service layer.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="object_perms",
        db_index=True,
    )
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, db_index=True
    )
    object_id = models.BigIntegerField(db_index=True)
    perm_codename = models.CharField(max_length=255, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "content_type", "object_id", "perm_codename"],
                name="uniq_user_object_perm",
            )
        ]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.perm_codename}:{self.content_type_id}:{self.object_id}"
