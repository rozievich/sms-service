from django.db import models
from django.contrib.auth.models import AbstractUser

from .validators import validate_phone_number


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=21, unique=True, validators=[validate_phone_number])


class Message(models.Model):
    message_text = models.CharField(max_length=255)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.message_id
