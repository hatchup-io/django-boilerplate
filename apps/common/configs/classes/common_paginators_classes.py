from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


def _unwrap_enveloped_schema(schema):
    """Return the inner data schema if the provided schema already includes our envelope."""

    if schema is None:
        return None

    response_schema = getattr(schema, "response", None)
    if response_schema is not None:
        return _unwrap_enveloped_schema(response_schema)

    if isinstance(schema, dict):
        if schema.get("type") == "object":
            data_schema = (schema.get("properties") or {}).get("data")
            if data_schema is not None:
                return data_schema
        return schema

    schema_type = getattr(schema, "type", None)
    if schema_type == "object":
        properties = getattr(schema, "properties", None) or {}
        if callable(properties):
            properties = properties()

        if isinstance(properties, dict):
            data_schema = properties.get("data")
            if data_schema is not None:
                return data_schema

    return schema


class DefaultPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 200

    def get_paginated_response(self, data):
        return Response(
            {
                "message": "Request was successful",
                "status": 200,
                "pagination": (
                    {
                        "links": {
                            "next": self.get_next_link(),
                            "previous": self.get_previous_link(),
                        },
                        "total_pages": self.page.paginator.num_pages,
                        "current_page": self.page.number,
                        "total_items": self.page.paginator.count,
                    }
                    if self.page.paginator.count > 0
                    else None
                ),
                "data": data,
            }
        )

    def get_paginated_response_schema(self, schema):
        data_schema = _unwrap_enveloped_schema(schema)

        return {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "status": {"type": "integer"},
                "pagination": {
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
                },
                "data": data_schema,
            },
        }
