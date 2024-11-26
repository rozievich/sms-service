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
    GetALLMessageAPIView,
    GetNickMeAPIView,
    GetMyBalanceAPIView,
    GetMessageCSVAPIView,
    UserModelViewSet
)

router = DefaultRouter()
router.register(r'users', UserModelViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path("get-secret-key/", GetSecretKeyAPIView.as_view(), name="get_secret_key"),
    path("refresh-secret-key/", RefreshSecretKeyAPIView.as_view(), name="refresh_secret_key"),
    path("my/profile/", GetProfileAPIView.as_view(), name="get_profile"),
    path("my/nicks/", GetNickMeAPIView.as_view(), name="nick_me"),
    path("my/balance/", GetMyBalanceAPIView.as_view(), name="my_balance"),
    path("sms/send/", SendSMSAPIView.as_view(), name="send_sms"),
    path("sms/send/all/", AllSendMessageAPIView.as_view(), name="all_user_send_sms"),
    path("sms/send/global/", InternationalSmsAPIView.as_view(), name="send_sms_global"),
    path("sms/get-user-messages/", GetALLMessageAPIView.as_view(), name="get_user_messages"),
    path("sms/csv/download/", GetMessageCSVAPIView.as_view(), name="csv_download"),
    path("sms/<str:message_id>/", SMSRetrieveAPIView.as_view(), name="get_sms")
]
