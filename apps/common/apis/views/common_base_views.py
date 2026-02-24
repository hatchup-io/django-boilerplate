from django.db.models import Q
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from apps.common.configs.classes.common_authentication_classes import (
    HatchupJWTAuthentication,
)
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


class HatchupBaseView(_SearchableQuerysetMixin, GenericAPIView):
    pagination_class = DefaultPagination
    authentication_classes = [HatchupJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def finalize_response(self, request, response, *args, **kwargs):
        """
        Wrap JSON responses in a success envelope,
        but leave streaming/binary responses untouched.
        """
        response = super().finalize_response(request, response, *args, **kwargs)

        if getattr(response, "streaming", False):
            return response

        if not isinstance(response, Response) or not hasattr(response, "data"):
            return response

        if getattr(response, "exception", False):
            return response

        if isinstance(response.data, dict):
            if "pagination" in response.data and "message" in response.data:
                return response

            if (
                hasattr(self, "action")
                and self.action == "list"
                and self.paginator is not None
                and isinstance(response.data, list)
            ):
                page = self.paginator.paginate_queryset(response.data, request)
                if page is not None:
                    return self.paginator.get_paginated_response(page)

            new_response = Response(
                {
                    "message": "Request was successful",
                    "status": response.status_code,
                    "pagination": None,
                    "data": response.data,
                },
                status=response.status_code,
            )
            new_response.accepted_renderer = response.accepted_renderer
            new_response.accepted_media_type = response.accepted_media_type
            new_response.renderer_context = response.renderer_context
            return new_response

        return response


class HatchupAPIView(HatchupBaseView, APIView):
    def finalize_response(self, request, response, *args, **kwargs):
        return super().finalize_response(request, response, *args, **kwargs)


class HatchupBaseViewset(_SearchableQuerysetMixin, GenericViewSet):
    pagination_class = DefaultPagination
    authentication_classes = [HatchupJWTAuthentication]
    permission_classes = []

    def finalize_response(self, request, response, *args, **kwargs):
        """
        Wrap JSON responses in a success envelope,
        but leave streaming/binary responses untouched.
        """
        response = super().finalize_response(request, response, *args, **kwargs)

        if getattr(response, "streaming", False):
            return response

        if not isinstance(response, Response) or not hasattr(response, "data"):
            return response

        if getattr(response, "exception", False):
            return response

        if isinstance(response.data, dict):
            if "pagination" in response.data and "message" in response.data:
                return response

            if (
                hasattr(self, "action")
                and self.action == "list"
                and self.paginator is not None
                and isinstance(response.data, list)
            ):
                page = self.paginator.paginate_queryset(response.data, request)
                if page is not None:
                    return self.paginator.get_paginated_response(page)

            new_response = Response(
                {
                    "message": "Request was successful",
                    "status": response.status_code,
                    "pagination": None,
                    "data": response.data,
                },
                status=response.status_code,
            )
            new_response.accepted_renderer = response.accepted_renderer
            new_response.accepted_media_type = response.accepted_media_type
            new_response.renderer_context = response.renderer_context
            return new_response

        return response


class HatchupReadViewset(HatchupBaseViewset, ListModelMixin, RetrieveModelMixin):
    pass


class HatchupUpsertViewset(
    HatchupBaseViewset, CreateModelMixin, UpdateModelMixin, DestroyModelMixin
):
    pass


class HatchupModelViewset(HatchupReadViewset, HatchupUpsertViewset):
    pass
