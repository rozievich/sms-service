from datetime import datetime
from rest_framework.exceptions import ValidationError
from rest_framework import serializers

from .models import Message, CustomUser, GlobalMessage


class CustomUserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"


class RefreshTokenSerializer(serializers.Serializer):
    secret_key = serializers.CharField(required=True)

    def validate_secret_key(self, value):
        if len(value) < 20:
            raise ValidationError("Secret key must be at least 10 characters long.")
        return value


class GetProfileSerilizer(serializers.Serializer):
    secret_key = serializers.CharField(required=True)

    def validate_secret_key(self, value):
        if len(value) < 20:
            raise ValidationError("Secret key must be at least 10 characters long.")
        return value


class MessageModelSerializer(serializers.ModelSerializer):
    secret_key = serializers.CharField(required=True, write_only=True)
    message_id = serializers.CharField(read_only=True)

    class Meta:
        model = Message
        fields = ("message_text", "message_id", "user", "created_at", "secret_key")

    def validate_secret_key(self, value):
        if len(value) < 20:
            raise ValidationError("Secret key must be at least 10 characters long.")
        return value

    def validate(self, attrs):
        user = attrs.get("user")
        try:
            user_info = CustomUser.objects.get(pk=user.id)
        except CustomUser.DoesNotExist:
            raise ValidationError("User not found.")        
        attrs['user_info'] = user_info
        return attrs


class AllSendMessageSerializer(serializers.Serializer):
    secret_key = serializers.CharField(max_length=500, required=True)
    message_text = serializers.CharField(max_length=255, required=True)

    def validate(self, attrs):
        if not attrs.get("secret_key") or not attrs.get("message_text"):
            raise ValidationError("Both secret_key and message_text are required.")
        return attrs


class InternationalSmsSerializer(serializers.ModelSerializer):
    secret_key = serializers.CharField(max_length=500, required=True, write_only=True)

    class Meta:
        model = GlobalMessage
        fields = "__all__"


class GetALLMessageSerializer(serializers.Serializer):
    secret_key = serializers.CharField(max_length=500, required=True)
    start_date = serializers.DateTimeField(required=True)
    end_date = serializers.DateTimeField(required=True)
    page_size = serializers.IntegerField(required=True)

    def validate_page_size(value):
        if not int(value) > 19 and not int(value) < 201:
            raise ValidationError("The value entered in page size must be greater than 20 and less than 200")
        return value

    def validate_start_date(value):
        try:
            datetime.strptime(value, "%Y-%m-%d %H:%M")
        except ValueError:
            raise serializers.ValidationError(
                "The time format is incorrect. Valid format: 'YYYY-MM-DD HH:MM'"
            )
        return value

    def validate_end_date(value):
        try:
            datetime.strptime(value, "%Y-%m-%d %H:%M")
        except ValueError:
            raise serializers.ValidationError(
                "The time format is incorrect. Valid format: 'YYYY-MM-DD HH:MM'"
            )
        return value
