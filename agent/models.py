from django.db import models

# Create your models here.


class Conversation(models.Model):
    id = models.AutoField(primary_key=True)
    wechat_id = models.CharField(max_length=100, db_index=True)
    messages = models.BinaryField()
    type = models.CharField(max_length=100)

    @staticmethod
    def add(wechat_id: str, messages: str, type: str) -> None:
        Conversation.objects.create(wechat_id=wechat_id, messages=messages, type=type)

    @staticmethod
    def delete(wechat_id: str) -> None:
        Conversation.objects.filter(wechat_id=wechat_id).delete()

    @staticmethod
    def get(wechat_id: str):
        conversation = Conversation.objects.filter(wechat_id=wechat_id).first()
        return conversation if conversation else None
