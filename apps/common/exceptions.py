"""
Domain exception hierarchy for use in services and selectors.

Raise these from `apps/<app>/services/*.py`. The DRF exception handler
(`apps.common.utils.common_exception_handler.hatchup_exception_handler`)
maps them to HTTP responses with the standard envelope.

Use these instead of generic `APIException` so that:
- the intent is explicit at the call site
- mapping to HTTP status codes is centralized
- views/serializers stay free of HTTP concerns
"""

from __future__ import annotations

from rest_framework.exceptions import APIException


class DomainError(APIException):
    """Base for application-level errors. Defaults to 400 Bad Request."""

    status_code = 400
    default_detail = "Request could not be completed."
    default_code = "domain_error"


class BusinessRuleError(DomainError):
    """A business rule was violated (vs. schema-level validation handled by serializers)."""

    status_code = 400
    default_detail = "Business rule violation."
    default_code = "business_rule_error"


class NotFoundError(DomainError):
    """The requested resource does not exist."""

    status_code = 404
    default_detail = "Resource not found."
    default_code = "not_found"


class ConflictError(DomainError):
    """The request conflicts with the current state of the resource."""

    status_code = 409
    default_detail = "Resource conflict."
    default_code = "conflict"


class PermissionDeniedError(DomainError):
    """The user is authenticated but not allowed to perform this action."""

    status_code = 403
    default_detail = "You do not have permission to perform this action."
    default_code = "permission_denied"
