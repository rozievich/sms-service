from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Message
from .serializers import LoginSerializer, RefreshTokenSerializer, GetProfileSerilizer, MessageModelSerializer

# Create your views here.
class GetSecretKeyAPIView(APIView):
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data, status.HTTP_200_OK)


class RefreshSecretKeyAPIView(APIView):
    permission_classes = (AllowAny, )

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

        return Response(serializer.validated_data, status.HTTP_200_OK)


class GetProfileAPIView(APIView):
    permission_classes = (AllowAny, )

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('secret_key', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True)
        ]
    )

    def get(self, request, *args, **kwargs):
        serializer = GetProfileSerilizer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data, status.HTTP_200_OK)


class SendSMSAPIView(ListCreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageModelSerializer
    permission_classes = (IsAuthenticated, )

