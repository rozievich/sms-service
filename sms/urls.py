from django.urls import path
from .views import GetSecretKeyAPIView, RefreshSecretKeyAPIView, GetProfileAPIView, SendSMSAPIView


urlpatterns = [
    path("get-secret-key/", GetSecretKeyAPIView.as_view(), name="get_secret_key"),
    path("refresh-secret-key/", RefreshSecretKeyAPIView.as_view(), name="refresh_secret_key"),
    path("get-profile/", GetProfileAPIView.as_view(), name="get_profile"),
    path("sms/send/", SendSMSAPIView.as_view(), name="send_sms")
]