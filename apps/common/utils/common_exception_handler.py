"""
Custom DRF exception handler so 5xx errors never expose internal details.
Responses use the standard envelope: { message, status, pagination, data }.
"""

from __future__ import annotations

import logging

from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)

GENERIC_SERVER_ERROR_MESSAGE = "An unexpected error occurred. Please try again later."


def hatchup_exception_handler(exc, context):
    """
    Call DRF's default handler first. For any 5xx or unhandled exception,
    return a generic envelope so clients never see stack traces or server details.
    """
    response = exception_handler(exc, context)

    if response is None:
        # Unhandled exception (e.g. not APIException) → 500, never expose details
        logger.exception("Unhandled exception in API view: %s", exc, exc_info=True)
        return Response(
            {
                "message": GENERIC_SERVER_ERROR_MESSAGE,
                "status": 500,
                "pagination": None,
                "data": None,
            },
            status=500,
        )

    # Replace 5xx response body with generic envelope so we never leak internals
    if response.status_code >= 500:
        logger.exception(
            "Server error in API view (status=%s): %s",
            response.status_code,
            exc,
            exc_info=True,
        )
        response.data = {
            "message": GENERIC_SERVER_ERROR_MESSAGE,
            "status": 500,
            "pagination": None,
            "data": None,
        }
        response.status_code = 500

    return response
