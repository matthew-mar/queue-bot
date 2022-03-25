from django.db import models


class Chats(models.Model):
    """ беседы групп """
    chat_vk_id = models.CharField(unique=True, null=True, max_length=20)
    chat_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.chat_name}"


class Admins(models.Model):
    """ старосты группы """
    admin_vk_id = models.CharField(unique=True, null=True, max_length=11)
    chat = models.ForeignKey(Chats, on_delete=models.CASCADE)


class Members(models.Model):
    """ участник """
    member_vk_id = models.CharField(unique=True, null=True, max_length=11)
    name = models.CharField(null=True, max_length=255)
    surname = models.CharField(null=True, max_length=255)

    def __str__(self):
        return f"{self.name} {self.surname}"


class ChatMembers(models.Model):
    """ учатсники бесед """
    chat = models.ForeignKey(Chats, on_delete=models.CASCADE)
    chat_member = models.ForeignKey(Members, on_delete=models.CASCADE, null=True)


class Queues(models.Model):
    """ очереди """
    member_order = models.IntegerField()
    queue_member = models.ForeignKey(Members, on_delete=models.CASCADE, null=True)


class QueuesChats(models.Model):
    """ промежуточная сущность между беседами и очередями """
    queue_datetime = models.DateTimeField()
    queue_name = models.CharField(max_length=255, null=True)
    chat = models.ForeignKey(Chats, on_delete=models.CASCADE)
    queue = models.ForeignKey(Queues, on_delete=models.CASCADE)
