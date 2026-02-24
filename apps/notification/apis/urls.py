from rest_framework.routers import DefaultRouter

from apps.notification.apis.views import NotificationViewSet

router = DefaultRouter()
router.register(r"", NotificationViewSet, basename="notifications")

urlpatterns = []
urlpatterns += router.urls
