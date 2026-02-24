from drf_spectacular.utils import OpenApiResponse
from drf_yasg import openapi


def base_schema_response(message):
    return OpenApiResponse(
        description=message,
        response=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "message": openapi.Schema(
                    type=openapi.TYPE_STRING, description=message
                ),
                "status": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="HTTP status code, e.g., 200 for success or 400 for failure",
                ),
                "pagination": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "links": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "next": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    description="URL for the next page, or null if there is no next page",
                                    nullable=True,
                                ),
                                "previous": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    description="URL for the previous page, or null if there is no previous page",
                                    nullable=True,
                                ),
                            },
                            description="Links for pagination navigation",
                            nullable=True,
                        ),
                        "total_pages": openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="Total number of pages",
                            nullable=True,
                        ),
                        "current_page": openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="Current page number",
                            nullable=True,
                        ),
                        "total_items": openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="Total number of items in the collection",
                            nullable=True,
                        ),
                    },
                    description="Pagination details or null if not applicable",
                    nullable=True,
                ),
                "data": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    description="Response data object or null if no data is available",
                    nullable=True,
                ),
            },
        ),
    )
