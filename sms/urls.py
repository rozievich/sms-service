from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GetSecretKeyAPIView,
    RefreshSecretKeyAPIView,
    GetProfileAPIView,
    SendSMSAPIView,
    SMSRetrieveAPIView,
    AllSendMessageAPIView,
    InternationalSmsAPIView,
    UserModelViewSet
)

router = DefaultRouter()
router.register(r'users', UserModelViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path("get-secret-key/", GetSecretKeyAPIView.as_view(), name="get_secret_key"),
    path("refresh-secret-key/", RefreshSecretKeyAPIView.as_view(), name="refresh_secret_key"),
    path("get-profile/", GetProfileAPIView.as_view(), name="get_profile"),
    path("sms/send/", SendSMSAPIView.as_view(), name="send_sms"),
    path("sms/send/all/", AllSendMessageAPIView.as_view(), name="all_user_send_sms"),
    path("sms/send/global/", InternationalSmsAPIView.as_view(), name="send_sms_global"),
    path("sms/<str:message_id>/", SMSRetrieveAPIView.as_view(), name="get_sms")
]
