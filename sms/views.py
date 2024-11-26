import requests
from uuid import uuid4
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser

from config.settings import SMS_FROM, SMS_EMAIL, SMS_API_KEY
from .models import Message, CustomUser, GlobalMessage
from .serializers import (
    RefreshTokenSerializer,
    GetProfileSerilizer,
    MessageModelSerializer,
    AllSendMessageSerializer,
    CustomUserModelSerializer,
    InternationalSmsSerializer,
    GetALLMessageSerializer
)


class UserModelViewSet(ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserModelSerializer
    permission_classes = (IsAuthenticated, )


class GetSecretKeyAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        payload = {"email": SMS_EMAIL, "password": SMS_API_KEY}
        response = requests.post("https://notify.eskiz.uz/api/auth/login", json=payload)
        if response.status_code != 200:
            return Response(response.json(), status=response.status_code)    
        return Response(response.json(), status=status.HTTP_200_OK)


class RefreshSecretKeyAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "secret_key": openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=['secret_key']
        )
    )

    def post(self, request, *args, **kwargs):
        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        secret_key = serializer.validated_data["secret_key"]
        headers = {"Authorization": f"Bearer {secret_key}"}
        response = requests.patch("https://notify.eskiz.uz/api/auth/refresh", headers=headers)

        if response.status_code != 200:
            return Response(response.json(), status=response.status_code)
        
        return Response(response.json(), status.HTTP_200_OK)


class GetProfileAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('secret_key', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True)
        ]
    )

    def get(self, request, *args, **kwargs):
        serializer = GetProfileSerilizer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        secret_key = serializer.validated_data['secret_key']

        headers = {"Authorization": f"Bearer {secret_key}"}
        response = requests.get("https://notify.eskiz.uz/api/auth/user", headers=headers)

        if response.status_code != 200:
            return Response(response.json(), status=response.status_code)

        return Response(response.json(), status.HTTP_200_OK)



class SendSMSAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "secret_key": openapi.Schema(type=openapi.TYPE_STRING),
                "message_text": openapi.Schema(type=openapi.TYPE_STRING),
                "user": openapi.Schema(type=openapi.TYPE_INTEGER)
            },
            required=['secret_key', 'message_text']
        )
    )

    def post(self, request, *args, **kwargs):
        serializer = MessageModelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_info = serializer.validated_data['user_info']
        message_text = serializer.validated_data['message_text']
        secret_key = serializer.validated_data['secret_key']

        payload = {
            "mobile_phone": user_info.phone[1:],
            "message": message_text,
            "from": SMS_FROM,
            "callback_url": "http://0000.uz/test.php"
        }
        headers = {"Authorization": f"Bearer {secret_key}"}

        try:
            response = requests.post("https://notify.eskiz.uz/api/message/sms/send", headers=headers, json=payload)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return Response({"error": f"Request failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        response_data = response.json()

        if response_data['status'] in ["success", "waiting"]:
            message = Message.objects.create(
                message_text=message_text,
                message_id=response_data.get('id'),
                user=user_info
            )
            return Response(response.json(), status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "Failed to send message."}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        messages = Message.objects.all()
        serializer = MessageModelSerializer(messages, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class SMSRetrieveAPIView(RetrieveAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageModelSerializer
    permission_classes = (IsAuthenticated, )
    lookup_field = 'message_id'


class AllSendMessageAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "secret_key": openapi.Schema(type=openapi.TYPE_STRING),
                "message_text": openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=['secret_key', 'message_text']
        )
    )

    def post(self, request, *args, **kwargs):
        serializer = AllSendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        secret_key = serializer.validated_data["secret_key"]
        message_text = serializer.validated_data["message_text"]

        data = {
            "messages": [
                {"user_sms_id": str(uuid4()), "to": user.phone[1:], "text": message_text}
                for user in CustomUser.objects.exclude(phone__isnull=True).exclude(phone__exact='')
            ],
            "from": SMS_FROM,
            "dispatch_id": str(uuid4())
        }
        headers = {"Authorization": f"Bearer {secret_key}"}
        response = requests.post("https://notify.eskiz.uz/api/message/sms/send-batch", json=data, headers=headers)

        if response.status_code != 200:
            return Response(response.json(), status=response.status_code)

        return Response(response.json(), status.HTTP_200_OK)


class InternationalSmsAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "secret_key": openapi.Schema(type=openapi.TYPE_STRING),
                "message_text": openapi.Schema(type=openapi.TYPE_STRING),
                "mobile_phone": openapi.Schema(type=openapi.TYPE_STRING),
                "country_code": openapi.Schema(type=openapi.TYPE_STRING)
            }
        )
    )

    def post(self, request, *args, **kwargs):
        serializer = InternationalSmsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        secret_key = serializer.validated_data.pop('secret_key')
        message_text = serializer.validated_data['message_text']
        mobile_phone = serializer.validated_data['mobile_phone']
        country_code = serializer.validated_data['country_code']

        payload={'mobile_phone': mobile_phone[1:], 'message': message_text, 'country_code': country_code, 'unicode': '0'}
        headers = {'Authorization': f'Bearer {secret_key}'}
        response = requests.post("https://notify.eskiz.uz/api/message/sms/send-global", headers=headers, json=payload)

        if response.status_code != 200:
            return Response({"error": response.json()}, status=response.status_code)

        serializer.save()
        return Response(response.json(), status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        messages = GlobalMessage.objects.all()
        serializer = InternationalSmsSerializer(messages, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class GetALLMessageAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        serializer = GetALLMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        secret_key = serializer.validated_data['secret_key']
        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data['end_date']
        page_size = serializer.validated_data['page_size']

        payload={'start_date': start_date.strftime('%Y-%m-%d %H:%M'), 'end_date': end_date.strftime('%Y-%m-%d %H:%M'), 'page_size': str(page_size), 'count': '0'}
        headers = {'Authorization': f'Bearer {secret_key}'}

        response = requests.post("https://notify.eskiz.uz/api/message/sms/get-user-messages", headers=headers, json=payload)
        if response.status_code != 200:
            return Response({"error": response.json()}, status=response.status_code)

        return Response(response.json(), status=status.HTTP_201_CREATED)


class GetNickMeAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('secret_key', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True)
        ]
    )

    def get(self, request, *args, **kwargs):
        secret_key = request.query_params.get("secret_key", None)
        if secret_key:
            headers = {'Authorization': f'Bearer {secret_key}'}
            response = requests.get("https://notify.eskiz.uz/api/nick/me", headers=headers)
            if response.status_code != 200:
                return Response(response.json(), status=response.status_code, safe=False)
            return Response(response.json(), status=status.HTTP_200_OK)
        return Response({"error": "secret key value not provided."}, status=status.HTTP_400_BAD_REQUEST)
