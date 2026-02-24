from django.urls import path

from apps.users.apis.views.user_views import CurrentUserAPIView, UserRegisterAPIView

urlpatterns = [
    path("register/", UserRegisterAPIView.as_view(), name="user-register"),
    path("me/", CurrentUserAPIView.as_view(), name="user-current"),
]
