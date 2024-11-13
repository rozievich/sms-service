import requests
from rest_framework.exceptions import ValidationError
from rest_framework import serializers

from .models import Message, CustomUser
from config.settings import SMS_EMAIL, SMS_API_KEY


class CustomUserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"


class LoginSerializer(serializers.Serializer):
    def validate(self, data):
        payload = {"email": SMS_EMAIL, "password": SMS_API_KEY}
        response = requests.post("https://notify.eskiz.uz/api/auth/login", json=payload)
        if response.status_code != 200:
            raise ValidationError("Invalid credentials or request failed.")
        return response.json()


class RefreshTokenSerializer(serializers.Serializer):
    secret_key = serializers.CharField(required=True)

    def validate(self, attrs):
        secret_key = attrs.get("secret_key", None)
        if not secret_key:
            raise ValidationError("Secret Key not entered")
        headers = {"Authorization": f"Bearer {secret_key}"}
        response = requests.patch("https://notify.eskiz.uz/api/auth/refresh", headers=headers)
        if response.status_code != 200:
            raise ValidationError("Invalid credentials or request failed.")
        return response.json()


class GetProfileSerilizer(serializers.Serializer):
    secret_key = serializers.CharField(required=True)

    def validate(self, attrs):
        secret_key = attrs.get("secret_key", None)
        if not secret_key:
            raise ValidationError("Secret Key not entered")
        headers = {"Authorization": f"Bearer {secret_key}"}
        response = requests.get("https://notify.eskiz.uz/api/auth/user", headers=headers)
        if response.status_code != 200:
            raise ValidationError("Invalid credentials or request failed.")
        return response.json()


class MessageModelSerializer(serializers.ModelSerializer):
    secret_key = serializers.CharField(required=True, write_only=True)
    message_id = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Message
        fields = ("message_text", "message_id", "user", "created_at", "status", "secret_key")


    def create(self, validated_data):
        secret_key = validated_data.pop("secret_key")
        message_text = validated_data.get("message_text")
        user = validated_data.get("user")

        try:
            user_info = CustomUser.objects.get(pk=user.id)
            payload = {
                "mobile_phone": user_info.phone[1:],
                "message": message_text,
                "from": "4546",
                "callback_url": "http://0000.uz/test.php"
            }
            headers = {"Authorization": f"Bearer {secret_key}"}

            # API ga so'rov yuborish
            response = requests.post("https://notify.eskiz.uz/api/message/sms/send", headers=headers, json=payload)
            if response.status_code != 200:
                raise ValidationError("Invalid credentials or request failed.")
            
            response_data = response.json()
            if response_data['status'] in ["success", "waiting"]:
                message = Message.objects.create(
                    message_text=message_text,
                    message_id=response_data.get('id'),
                    user=user_info,
                    status=response_data['status']
                )
                return message
            else:
                raise ValidationError("Failed to send message.")

        except CustomUser.DoesNotExist:
            raise ValidationError("User not found.")
