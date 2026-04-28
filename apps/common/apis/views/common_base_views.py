from django.db.models import Q
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin
from rest_framework.mixins import DestroyModelMixin
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from apps.common.configs.classes.common_authentication_classes import HatchupJWTAuthentication
from apps.common.configs.classes.common_paginators_classes import DefaultPagination


class _SearchableQuerysetMixin:
    search_param = "search"
    search_fields = ()

    def get_search_fields(self):
        return tuple(getattr(self, "search_fields", ()))

    def apply_search_filter(self, queryset, request):
        search_query = request.query_params.get(self.search_param, "").strip()
        search_fields = self.get_search_fields()

        if not search_query or not search_fields:
            return queryset

        search_filter = Q()
        for field in search_fields:
            search_filter |= Q(**{f"{field}__icontains": search_query})

        return queryset.filter(search_filter)


def _envelope_message_and_data(status_code, data):
    """
    Build (message, data) for the response envelope.

    For 4xx/5xx with a `detail` key, surface that as the message and drop it from data.
    For other 4xx with field errors, surface the first error string.
    For success, use the standard success message.
    """
    if status_code >= 400 and isinstance(data, dict):
        detail = data.get("detail")
        if detail is not None:
            if isinstance(detail, list):
                message = detail[0] if detail else "Request failed"
            else:
                message = detail
            return message, None
        if data:
            first_key = next(iter(data), None)
            if first_key is not None:
                first_errors = data[first_key]
                if isinstance(first_errors, list) and first_errors:
                    message = first_errors[0]
                elif isinstance(first_errors, str):
                    message = first_errors
                else:
                    message = "Validation error."
                return message, data
        return "Request failed", data
    return "Request was successful", data


class _EnvelopeFinalizeMixin:
    """
    Wraps JSON responses in the standard envelope:
        { message, status, pagination, data }

    Streaming/binary responses and already-enveloped responses pass through.
    Pagination is honored: paginated list views surface pagination metadata.
    """

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)

        if getattr(response, "streaming", False):
            return response

        if not isinstance(response, Response) or not hasattr(response, "data"):
            return response

        if isinstance(response.data, dict) and "pagination" in response.data and "message" in response.data:
            return response

        if (
            hasattr(self, "action")
            and getattr(self, "action", None) == "list"
            and getattr(self, "paginator", None) is not None
            and isinstance(response.data, list)
        ):
            page = self.paginator.paginate_queryset(response.data, request)
            if page is not None:
                return self.paginator.get_paginated_response(page)

        message, data = _envelope_message_and_data(response.status_code, response.data)
        new_response = Response(
            {
                "message": message,
                "status": response.status_code,
                "pagination": None,
                "data": data,
            },
            status=response.status_code,
        )
        new_response.accepted_renderer = response.accepted_renderer
        new_response.accepted_media_type = response.accepted_media_type
        new_response.renderer_context = response.renderer_context
        return new_response


class HatchupBaseView(_SearchableQuerysetMixin, _EnvelopeFinalizeMixin, GenericAPIView):
    pagination_class = DefaultPagination
    authentication_classes = [HatchupJWTAuthentication]
    permission_classes = [IsAuthenticated]


class HatchupAPIView(HatchupBaseView, APIView):
    pass


class HatchupBaseViewset(_SearchableQuerysetMixin, _EnvelopeFinalizeMixin, GenericViewSet):
    pagination_class = DefaultPagination
    authentication_classes = [HatchupJWTAuthentication]
    permission_classes = []


class HatchupReadViewset(HatchupBaseViewset, ListModelMixin, RetrieveModelMixin):
    pass


class HatchupUpsertViewset(HatchupBaseViewset, CreateModelMixin, UpdateModelMixin, DestroyModelMixin):
    pass


class HatchupModelViewset(HatchupReadViewset, HatchupUpsertViewset):
    pass
