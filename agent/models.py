from django.db import models

# Create your models here.


class Conversation(models.Model):
    id = models.AutoField(primary_key=True)
    wechat_id = models.CharField(max_length=100, unique=True, db_index=True)
    messages = models.BinaryField()
    type = models.CharField(max_length=100)
