from django.db import models


class Chat(models.Model):
    """ беседы групп """
    chat_vk_id = models.CharField(unique=True, null=True, max_length=20)
    chat_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.chat_name}"


class Member(models.Model):
    """ участник """
    member_vk_id = models.CharField(unique=True, null=True, max_length=11)
    name = models.CharField(null=True, max_length=255)
    surname = models.CharField(null=True, max_length=255)

    def __str__(self):
        return f"{self.name} {self.surname}"


class ChatMember(models.Model):
    """ учатсники бесед """
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    chat_member = models.ForeignKey(Member, on_delete=models.CASCADE, null=True)
    is_admin = models.BooleanField(default=False)


class Queue(models.Model):
    """ очереди """
    member_order = models.IntegerField(null=True)
    queue_member = models.ForeignKey(Member, on_delete=models.CASCADE, null=True)


class QueueChat(models.Model):
    """ промежуточная сущность между беседами и очередями """
    queue_datetime = models.DateTimeField()
    queue_name = models.CharField(max_length=255, null=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    queue = models.ForeignKey(Queue, on_delete=models.CASCADE)
