import requests
from io import BytesIO
from uuid import uuid4
from django.http import FileResponse
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from config.settings import SMS_FROM, SMS_EMAIL, SMS_API_KEY
from .models import Message, CustomUser, GlobalMessage, SecretKey
from .serializers import (
    MessageModelSerializer,
    AllSendMessageSerializer,
    CustomUserModelSerializer,
    InternationalSmsSerializer,
    GetALLMessageSerializer,
    GetMessageCSVSerializer
)


class UserModelViewSet(ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserModelSerializer
    permission_classes = (IsAuthenticated, )


class SecretKeyAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        payload = {"email": SMS_EMAIL, "password": SMS_API_KEY}
        response = requests.post("https://notify.eskiz.uz/api/auth/login", json=payload)
        if response.status_code == 200:
            SecretKey.objects.create(secret_key=response.json()['data']['token'])
            return Response({"status": True, "message": "Secret key created successfully"}, status=status.HTTP_201_CREATED)
        return Response(response.json(), status=response.status_code)

    def patch(self, request, *args, **kwargs):
        secret_key = SecretKey.objects.first()
        if not secret_key:
            return Response({"status": False, "Message": "The private key data has not been created, please create it first."}, status=status.HTTP_404_NOT_FOUND)
        
        headers = {"Authorization": f"Bearer {secret_key.secret_key}"}
        response = requests.patch("https://notify.eskiz.uz/api/auth/refresh", headers=headers)
        if response.status_code == 200:
            secret_key.secret_key = response.json()['data']['token']
            secret_key.save()
            return Response({"status": True, "message": "Secret key update successfully"}, status=status.HTTP_206_PARTIAL_CONTENT)
        return Response(response.json(), status=response.status_code)


class GetProfileAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        secret_key = SecretKey.objects.first()
        headers = {"Authorization": f"Bearer {secret_key.secret_key}"}
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
                "message_text": openapi.Schema(type=openapi.TYPE_STRING),
                "user": openapi.Schema(type=openapi.TYPE_INTEGER)
            },
            required=['message_text']
        )
    )

    def post(self, request, *args, **kwargs):
        serializer = MessageModelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_info = serializer.validated_data['user_info']
        message_text = serializer.validated_data['message_text']
        secret_key = SecretKey.objects.first()

        payload = {
            "mobile_phone": user_info.phone[1:],
            "message": message_text,
            "from": SMS_FROM,
            "callback_url": "http://0000.uz/test.php"
        }
        headers = {"Authorization": f"Bearer {secret_key.secret_key}"}

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
                "message_text": openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=['message_text']
        )
    )

    def post(self, request, *args, **kwargs):
        serializer = AllSendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        secret_key = SecretKey.objects.first()
        message_text = serializer.validated_data["message_text"]

        data = {
            "messages": [
                {"user_sms_id": str(uuid4()), "to": user.phone[1:], "text": message_text}
                for user in CustomUser.objects.exclude(phone__isnull=True).exclude(phone__exact='')
            ],
            "from": SMS_FROM,
            "dispatch_id": str(uuid4())
        }
        headers = {"Authorization": f"Bearer {secret_key.secret_key}"}
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
                "message_text": openapi.Schema(type=openapi.TYPE_STRING),
                "mobile_phone": openapi.Schema(type=openapi.TYPE_STRING),
                "country_code": openapi.Schema(type=openapi.TYPE_STRING)
            }
        )
    )

    def post(self, request, *args, **kwargs):
        serializer = InternationalSmsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message_text = serializer.validated_data['message_text']
        mobile_phone = serializer.validated_data['mobile_phone']
        country_code = serializer.validated_data['country_code']
        secret_key = SecretKey.objects.first()

        payload={'mobile_phone': mobile_phone[1:], 'message': message_text, 'country_code': country_code, 'unicode': '0'}
        headers = {'Authorization': f'Bearer {secret_key.secret_key}'}
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

        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data['end_date']
        page_size = serializer.validated_data['page_size']
        secret_key = SecretKey.objects.first()

        payload={'start_date': start_date.strftime('%Y-%m-%d %H:%M'), 'end_date': end_date.strftime('%Y-%m-%d %H:%M'), 'page_size': str(page_size), 'count': '0'}
        headers = {'Authorization': f'Bearer {secret_key.secret_key}'}

        response = requests.post("https://notify.eskiz.uz/api/message/sms/get-user-messages", headers=headers, json=payload)
        if response.status_code != 200:
            return Response({"error": response.json()}, status=response.status_code)

        return Response(response.json(), status=status.HTTP_201_CREATED)


class GetNickMeAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        secret_key = SecretKey.objects.first()
        if secret_key:
            headers = {'Authorization': f'Bearer {secret_key.secret_key}'}
            response = requests.get("https://notify.eskiz.uz/api/nick/me", headers=headers)
            if response.status_code != 200:
                return Response(response.json(), status=response.status_code, safe=False)
            return Response(response.json(), status=status.HTTP_200_OK)
        return Response({"error": "secret key value not provided."}, status=status.HTTP_400_BAD_REQUEST)


class GetMyBalanceAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        secret_key = SecretKey.objects.first()
        if not secret_key:
            return Response({"error": "secret key value not provided."}, status=status.HTTP_400_BAD_REQUEST)
        headers = {"Authorization": f"Bearer {secret_key.secret_key}"}
        response = requests.get("https://notify.eskiz.uz/api/user/get-limit", headers=headers)
        if response.status_code != 200:
            return Response(response.json(), status=response.status_code, safe=False)
        return Response(response.json(), status=status.HTTP_200_OK)


class GetMessageCSVAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties = {
                "year": openapi.Schema(type=openapi.TYPE_INTEGER),
                "month": openapi.Schema(type=openapi.TYPE_INTEGER),
                "start_day": openapi.Schema(type=openapi.TYPE_INTEGER),
                "end_day": openapi.Schema(type=openapi.TYPE_INTEGER),
                "status": openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=['year', 'month', 'status']
        )
    )

    def post(self, request, *args, **kwargs):
        serializer = GetMessageCSVSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        secret_key = SecretKey.objects.first()
        year = serializer.validated_data['year']
        month = serializer.validated_data['month']
        start_day = serializer.validated_data.get('start_day')
        end_day = serializer.validated_data.get('end_day')
        status_ = serializer.validated_data['status']

        payload = {"year": year, "month": month, "start": f"{year}-{month}-{start_day} 00:00:00" if start_day else "", "end": f"{year}-{month}-{end_day} 00:00:00" if end_day else ""}
        headers = {"Authorization": f"Bearer {secret_key.secret_key}"}

        response = requests.post(f"https://notify.eskiz.uz/api/message/export?status={status_}", data=payload, headers=headers)
        if response.status_code == 200:
            file_stream = BytesIO(response.content)
            file_stream.seek(0)
            return FileResponse(file_stream, as_attachment=True, filename="exported_file.csv", content_type="text/csv")
        return Response(response.json(), status=response.status_code)
