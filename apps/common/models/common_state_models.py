"""Re-export state models from common_workflow_models for backward compatibility."""

from apps.common.models.common_workflow_models import StateTransitionLog
from apps.common.models.common_workflow_models import StateTransitionMixin

__all__ = ["StateTransitionLog", "StateTransitionMixin"]
