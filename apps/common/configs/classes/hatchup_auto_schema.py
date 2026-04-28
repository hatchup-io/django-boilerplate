"""
Custom drf-spectacular AutoSchema that wraps success response schemas in the standard
envelope (message, status, pagination, data) to match finalize_response in common_base_views.
"""

from __future__ import annotations

from drf_spectacular.openapi import AutoSchema
from drf_spectacular.plumbing import get_class
from drf_spectacular.plumbing import get_list_serializer
from drf_spectacular.plumbing import is_list_serializer

from apps.common.apis.serializers.common_envelope_serializers import build_envelope_serializer

# OpenAPI schema fragment for the standard envelope (matches finalize_response).
ENVELOPE_PAGINATION_SCHEMA = {
    "type": "object",
    "nullable": True,
    "properties": {
        "links": {
            "type": "object",
            "properties": {
                "next": {"type": "string", "nullable": True},
                "previous": {"type": "string", "nullable": True},
            },
        },
        "total_pages": {"type": "integer", "nullable": True},
        "current_page": {"type": "integer", "nullable": True},
        "total_items": {"type": "integer", "nullable": True},
    },
}


def _build_envelope_schema(data_schema):
    """Wrap a schema in the standard envelope (message, status, pagination, data)."""
    return {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "Human-readable success message.",
            },
            "status": {"type": "integer", "description": "HTTP status code."},
            "pagination": ENVELOPE_PAGINATION_SCHEMA,
            "data": data_schema,
        },
        "required": ["message", "status", "pagination", "data"],
    }


def _inner_serializer_class_and_many(serializer):
    """Resolve (serializer_class, many) for envelope wrapping."""
    if is_list_serializer(serializer):
        list_ser = get_list_serializer(serializer)
        return get_class(list_ser.child), True
    return get_class(serializer), False


class HatchupAutoSchema(AutoSchema):
    """
    Wraps 2xx response schemas in the standard envelope so Swagger matches
    the actual API response shape (finalize_response in common_base_views).
    List views with pagination are left unchanged (DefaultPagination
    already returns the envelope).
    """

    def get_response_serializers(self):
        result = super().get_response_serializers()
        if result is None:
            return None

        paginator = self._get_paginator()
        is_list = self._is_list_view(result)
        skip_wrap = is_list and paginator is not None

        if skip_wrap:
            return result

        if isinstance(result, dict):
            wrapped = {}
            for code, serializer in result.items():
                code_str = str(code) if not isinstance(code, tuple) else str(code[0])
                if code_str.startswith("2") and code_str != "204":
                    inner_class, many = _inner_serializer_class_and_many(serializer)
                    wrapped[code] = build_envelope_serializer(inner_class, many=many)()
                else:
                    wrapped[code] = serializer
            return wrapped

        inner_class, many = _inner_serializer_class_and_many(result)
        return build_envelope_serializer(inner_class, many=many)()

    def _get_response_for_code(self, serializer, status_code, media_types=None, direction="response"):
        response = super()._get_response_for_code(serializer, status_code, media_types=media_types, direction=direction)
        if not response or "content" not in response:
            return response
        code = str(status_code)
        if not (code.startswith("2") and code != "204"):
            return response
        paginator = self._get_paginator()
        if self._is_list_view(serializer) and paginator is not None:
            return response
        for content in response["content"].values():
            inner = content.get("schema")
            if not inner:
                continue
            if isinstance(inner, dict) and set(inner.get("properties") or {}).issuperset(
                {"message", "status", "pagination", "data"}
            ):
                continue
            content["schema"] = _build_envelope_schema(inner)
        return response
