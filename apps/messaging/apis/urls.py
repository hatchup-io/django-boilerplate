from rest_framework.routers import DefaultRouter

from apps.messaging.apis.views.messaging_viewsets import ConversationViewSet


router = DefaultRouter()
router.register(r"conversations", ConversationViewSet, basename="conversation")

urlpatterns = []
urlpatterns += router.urls
