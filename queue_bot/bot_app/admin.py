from django.contrib import admin
from .models import Chats, Admins, ChatMembers, Queues, QueuesChats, Members


class MemberAdmin(admin.ModelAdmin):
    list_display = ["name", "surname"]


class ChatsAdmin(admin.ModelAdmin):
    list_display = ["chat_name"]


class AdminsAdmin(admin.ModelAdmin):
    list_display = ["chat"]


class ChatMembersAdmin(admin.ModelAdmin):
    list_display = ["chat_member"]


class QueuesAdmin(admin.ModelAdmin):
    list_display = ["member_order", "queue_member"]


class QueuesChatsAdmin(admin.ModelAdmin):
    list_display = ["queue_datetime", "queue_name", "chat"]


admin.site.register(Members, MemberAdmin)
admin.site.register(Admins, AdminsAdmin)
admin.site.register(Chats, ChatsAdmin)
admin.site.register(ChatMembers, ChatMembersAdmin)
admin.site.register(Queues, QueuesAdmin)
admin.site.register(QueuesChats, QueuesChatsAdmin)
