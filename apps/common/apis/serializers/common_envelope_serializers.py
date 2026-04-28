"""
Serializers for the standard API response envelope used by finalize_response in base views.

All successful JSON responses are wrapped as:
  { "message": str, "status": int, "pagination": object | null, "data": ... }
"""

from __future__ import annotations

from rest_framework import serializers


class PaginationLinksSerializer(serializers.Serializer):
    """Schema for pagination links."""

    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)


class PaginationSerializer(serializers.Serializer):
    """Schema for pagination block (used when list is paginated)."""

    links = PaginationLinksSerializer(allow_null=True)
    total_pages = serializers.IntegerField(allow_null=True)
    current_page = serializers.IntegerField(allow_null=True)
    total_items = serializers.IntegerField(allow_null=True)


def build_envelope_serializer(inner_serializer_class, many: bool = False, component_name: str | None = None):
    """
    Build a serializer class that wraps the given serializer in the standard envelope
    (message, status, pagination, data) to match finalize_response in common_base_views.

    Used by HatchupAutoSchema so Swagger documents the real response shape.
    """
    from drf_spectacular.utils import extend_schema_serializer

    name = component_name
    if name is None:
        base = getattr(inner_serializer_class, "__name__", "Data")
        if isinstance(base, str) and "Serializer" in base:
            base = base.replace("Serializer", "").strip() or "Data"
        suffix = "List" if many else ""
        name = f"Envelope{base}{suffix}"

    @extend_schema_serializer(component_name=name)
    class EnvelopeSerializer(serializers.Serializer):
        message = serializers.CharField(help_text="Human-readable success message.")
        status = serializers.IntegerField(help_text="HTTP status code.")
        pagination = PaginationSerializer(allow_null=True)
        data = inner_serializer_class(many=many)

    return EnvelopeSerializer
