from django.contrib import admin
from bot_app.models import Chat, ChatMember, Queue, QueueChat, Member


class MemberAdmin(admin.ModelAdmin):
    list_display = ["name", "surname"]


class ChatsAdmin(admin.ModelAdmin):
    list_display = ["chat_name"]


class AdminsAdmin(admin.ModelAdmin):
    list_display = ["chat"]


class ChatMembersAdmin(admin.ModelAdmin):
    list_display = ["chat", "chat_member", "is_admin"]


class QueuesAdmin(admin.ModelAdmin):
    list_display = ["member_order", "queue_member"]


class QueuesChatsAdmin(admin.ModelAdmin):
    list_display = ["queue_datetime", "queue_name", "chat"]


admin.site.register(Member, MemberAdmin)
admin.site.register(Chat, ChatsAdmin)
admin.site.register(ChatMember, ChatMembersAdmin)
admin.site.register(Queue, QueuesAdmin)
admin.site.register(QueueChat, QueuesChatsAdmin)
