from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.common.apis.views.common_health_views import (
    HatchupHealthCheckView,
    HatchupReadinessView,
)


router = DefaultRouter()

urlpatterns = [
    path("health/", HatchupHealthCheckView.as_view(), name="health-check"),
    path("readiness/", HatchupReadinessView.as_view(), name="readiness"),
]
urlpatterns += router.urls
