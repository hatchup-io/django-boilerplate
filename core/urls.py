from django.conf import settings
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

from apps.common.admins import admin_site
from django.conf.urls.static import static

THIRD_PARTY_URLS = [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("ckeditor5/", include("django_ckeditor_5.urls")),
]


APP_URLS = [
    path("auth/", include("apps.auth.apis.urls")),
    path("users/", include("apps.users.apis.urls")),
    path("document/", include("apps.document.apis.urls")),
]


urlpatterns = [
    path("admin/", admin_site.urls),
    path("api/", include(APP_URLS)),
    path("", include(THIRD_PARTY_URLS)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
