from common.apis.views.common_base_views import HatchupAPIView
from common.utils.common_health_check_utils import (
    basic_health_payload,
    ready_health_payload,
)
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema


class HatchupHealthCheckView(HatchupAPIView):
    authentication_classes: tuple = ()
    permission_classes: tuple = ()

    @extend_schema(
        tags=["Health"],
        summary="health checl",
    )
    def get(self, request, *args, **kwargs):
        data = basic_health_payload()
        print("PRINT", data)
        return Response(data, status=200)


class HatchupReadinessView(HatchupAPIView):
    authentication_classes: tuple = ()
    permission_classes: tuple = ()

    @extend_schema(
        tags=["Health"],
        summary="Service readiness",
        description="Performs connectivity checks for Redis, cache, RabbitMQ, and Celery.",
    )
    def get(self, request):
        payload, status_code = ready_health_payload()
        return Response(payload, status=status_code)
