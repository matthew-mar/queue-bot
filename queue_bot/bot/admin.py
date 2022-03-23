from django.contrib import admin
from .models import Chats, Admins, ChatMembers, Queues, QueuesChats


class ChatsAdmin(admin.ModelAdmin):
    pass


class AdminsAdmin(admin.ModelAdmin):
    pass


class ChatMembersAdmin(admin.ModelAdmin):
    pass


class QueuesAdmin(admin.ModelAdmin):
    pass


class QueuesChatsAdmin(admin.ModelAdmin):
    pass


admin.site.register(Chats, ChatsAdmin)
admin.site.register(Admins, AdminsAdmin)
admin.site.register(ChatMembers, ChatMembersAdmin)
admin.site.register(Queues, QueuesAdmin)
admin.site.register(QueuesChats, QueuesChatsAdmin)
