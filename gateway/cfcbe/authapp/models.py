from django.db import models

# Create your models here.
import pyotp
import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, whatsapp_number):
        user = self.model(whatsapp_number=whatsapp_number)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    whatsapp_number = models.CharField(max_length=15, unique=True)
    otp_secret = models.CharField(max_length=32, default=pyotp.random_base32)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'whatsapp_number'

    def generate_otp(self):
        return pyotp.TOTP(self.otp_secret).now()
