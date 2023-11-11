from django.db import models
from datetime import datetime, timedelta
import secrets
import jwt


# Create your models here.


class User(models.Model):
    token_expiring_time = 3600
    JWT_expire_time = 3600 * 24

    id = models.AutoField(primary_key=True)
    wechat_id = models.CharField(max_length=100, unique=True)
    nickname = models.CharField(max_length=100)

    temp_token = models.CharField(max_length=100, unique=True, null=True)
    temp_token_expires = models.DateTimeField(null=True)

    def serialize(self):
        return {
            'id': self.id,
            'wechat_id': self.wechat_id,
            'nickname': self.nickname,
        }

    def generate_temp_token(self):
        token = secrets.token_urlsafe(32)
        while User.objects.filter(temp_token=token).exists():
            token = secrets.token_urlsafe(32)
        self.temp_token = token
        self.temp_token_expires = datetime.now() + timedelta(seconds=self.token_expiring_time)
        self.save()

    def generate_JWT(self):
        payload = {
            'user': self.serialize(),
            'generate_time': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
