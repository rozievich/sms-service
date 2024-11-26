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
    start_date = serializers.DateTimeField(required=True, format="%Y-%m-%d %H:%M", input_formats=['%Y-%m-%d %H:%M'])
    end_date = serializers.DateTimeField(required=True, format="%Y-%m-%d %H:%M", input_formats=['%Y-%m-%d %H:%M'])
    page_size = serializers.IntegerField(required=True)

    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise ValidationError("Start date cannot be greater than end date.")
        return data
    
    def validate_page_size(self, value):
        if value < 19 and value > 201:
            raise ValidationError("The value entered in page size must be greater than 20 and less than 200")
        return value


class GetMessageCSVSerializer(serializers.Serializer):
    secret_key = serializers.CharField(max_length=500, required=True)
    year = serializers.IntegerField(required=True)
    month = serializers.IntegerField(required=True)
    start_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", input_formats=["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", ""])
    end_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", input_formats=["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", ""])
    status = serializers.CharField(max_length=30, required=True)

    def validate(self, attrs):
        start_date = attrs.get('start_date', None)
        end_date = attrs.get('end_date', None)
        if start_date and end_date:
            if start_date > end_date and end_date > datetime.now().strftime("%Y:%m:%d %H:%M:%S"):
                raise ValidationError("Start date cannot be greater than end date.")
        return attrs

    def validate_secret_key(self, value):
        if len(value) < 20:
            raise ValidationError("Both secret_key and message_text are required.")
        return value

    def validate_year(self, value):
        now_year = datetime.now().strftime("%Y")
        if value > int(now_year) and value < 1900:
            raise ValidationError(f"The Year attribute must be greater than 1900 and less than {now_year}.")
        return value

    def validate_month(self, value):
        if value > 12 and value < 1:
            raise ValidationError("The month attribute must be less than 12 and greater than 0.")
        return value

    def validate_status(self, value):
        if value not in ["all", "delivered", "rejected"]:
            raise ValidationError("This state is not supported. Example: all, submitted, rejected")
        return value
