from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django_fsm import can_proceed

from common.models.common_base_models import HatchUpBaseModel


class StateTransitionLog(HatchUpBaseModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    from_state = models.CharField(max_length=64)
    to_state = models.CharField(max_length=64)
    transition = models.CharField(max_length=64)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="state_transition_logs",
    )
    notes = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(
                fields=["content_type", "object_id"], name="state_log_obj_idx"
            ),
            models.Index(fields=["created_at"], name="state_log_created_idx"),
        ]

    def __str__(self) -> str:
        return (
            f"{self.content_type.model}:{self.object_id} "
            f"{self.from_state}->{self.to_state}"
        )


class StateTransitionMixin(models.Model):
    """
    Shared helper to run transitions and record history.
    """

    state_history = GenericRelation(
        "common.StateTransitionLog",
        related_query_name="stateful_object",
    )

    class Meta:
        abstract = True

    def _has_model_field(self, field_name: str) -> bool:
        return any(field.name == field_name for field in self._meta.fields)

    def record_transition(
        self, *, from_state: str, to_state: str, transition: str, by=None, notes=None
    ):
        def _normalize_state(value):
            if hasattr(value, "code"):
                return value.code
            return value or ""

        StateTransitionLog.objects.create(
            content_object=self,
            from_state=_normalize_state(from_state),
            to_state=_normalize_state(to_state),
            transition=transition,
            actor=by if getattr(by, "is_authenticated", False) else None,
            notes=notes or "",
        )

    def apply_transition(
        self, transition_name: str, *, by=None, notes=None, state_field=None, **kwargs
    ):
        transition_method = getattr(self, transition_name, None)
        if transition_method is None:
            raise ValidationError(f"Unknown transition '{transition_name}'.")

        resolved_field = state_field or getattr(
            self, "transition_state_fields", {}
        ).get(transition_name)

        if not can_proceed(transition_method):
            raise ValidationError(
                f"Transition '{transition_name}' is not allowed from '{self.state}'."
            )

        from_state = (
            getattr(self, resolved_field)
            if resolved_field
            else getattr(self, "state", None)
        )
        transition_method(by=by, notes=notes, **kwargs)
        to_state = (
            getattr(self, resolved_field)
            if resolved_field
            else getattr(self, "state", None)
        )

        update_fields = []
        if resolved_field:
            update_fields.append(resolved_field)
        elif self._has_model_field("state"):
            update_fields.append("state")
        if hasattr(self, "updated_at"):
            update_fields.append("updated_at")
        if hasattr(self, "stage"):
            update_fields.append("stage")
        self.save(update_fields=update_fields)

        self.record_transition(
            from_state=from_state,
            to_state=to_state,
            transition=transition_name,
            by=by,
            notes=notes,
        )
        return self
