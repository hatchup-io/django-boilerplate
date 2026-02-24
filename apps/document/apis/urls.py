from rest_framework.routers import DefaultRouter

from apps.document.apis.views import DocumentViewSet

router = DefaultRouter()
router.register(r"", DocumentViewSet, basename="document")

urlpatterns = []
urlpatterns += router.urls
