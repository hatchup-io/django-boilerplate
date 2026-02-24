from django.urls import path

from auth.apis.views.auth_login_views import LoginAPIView
from auth.apis.views.auth_login_views import RefreshTokenAPIView
from auth.apis.views.otp_views import OTPRequestView
from auth.apis.views.otp_views import OTPTokenExchangeView
from auth.apis.views.otp_views import OTPVerifyView

urlpatterns = [
    path("token/", LoginAPIView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", RefreshTokenAPIView.as_view(), name="token_refresh"),
    path("otp/request/", OTPRequestView.as_view(), name="otp_request"),
    path("otp/verify/", OTPVerifyView.as_view(), name="otp_verify"),
    path("otp/token/", OTPTokenExchangeView.as_view(), name="otp_token"),
]
