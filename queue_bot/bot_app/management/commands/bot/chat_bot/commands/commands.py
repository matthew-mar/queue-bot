import json
from pprint import pprint
from typing import Any
from bot_app.management.commands.bot.bot_commands.command import BotCommand
from bot_app.management.commands.bot.bot_commands.commands_exceptions import ChatAlreadySavedError, ChatBotIsNotAdminError
from bot_app.management.commands.bot.bot_middlewares.db_middlewares import connect_chat_with_members, get_new_chat, save_chat, save_chat_member, save_members
from bot_app.management.commands.bot.bot_middlewares.middlewares import is_admin
from bot_app.management.commands.bot.bot_middlewares.vk_api_middlewares import get_chat_members, get_conversation
from bot_app.management.commands.bot.dialog_bot.messages import ChatInvitationMessages, ChatStartMessages
from bot_app.management.commands.bot.vk_api.longpoll.responses import ConversationsResponse, Event, MembersResponse, Profile, UserResponse
from bot_app.management.commands.bot.vk_api.keyboard.keyboard import Button, make_keyboard
from bot_app.models import Chat, ChatMember, Member, Queue, QueueChat


class ChatInvitationCommand(BotCommand):
    """ команда приглашения в беседу """
    def __init__(self) -> None:
        super().__init__()
    
    def start(self, event: Event, **kwargs) -> Any:
        super().start(event=event, **kwargs)
    
    def start_action(self, event: Event) -> None:
        self.api.messages.send(
            peer_id=event.peer_id,
            message=ChatInvitationMessages.START_MESSAGE,
            keyboard=make_keyboard(
                inline=False,
                buttons=[Button(label="start").button_json]
            )
        )
        self.end(event)


class ChatStartCommand(BotCommand):
    """ команда "start" в беседеах """
    def __init__(self) -> None:
        super().__init__()

    def start(self, event: Event, **kwargs) -> Any:
        super().start(event=event, **kwargs)

    def start_action(self, event: Event) -> None:
        # получение информации о беседе
        conversation: ConversationsResponse = get_conversation(peer_id=event.peer_id)
        # получение участников беседы
        if is_admin(conversation):
            members: MembersResponse = get_chat_members(peer_id=event.peer_id)
            try:
                save_chat_member(
                    conversation=conversation,
                    members=members
                )
                self.api.messages.send(
                    peer_id=event.peer_id,
                    message=ChatStartMessages.CHAT_SAVED_MESSAGE
                )
            except ChatAlreadySavedError as exception:
                self.api.messages.send(
                    peer_id=event.peer_id,
                    message=exception.args[0]
            )
        else:
            self.api.messages.send(
                peer_id=event.peer_id,
                message=ChatStartMessages.NOT_ADMIN_ERROR_MESSAGE
            )
        self.end(event) 


class CickUserCommand(BotCommand):
    """ команда удаления пользователя из беседы """
    def __init__(self) -> None:
        super().__init__()
    
    def start(self, event: Event, **kwargs) -> Any:
        """ удаление связи между пользователем и беседой """
        kicked_member: Member = Member.objects.filter(
            member_vk_id=event.action["member_id"]
        )[0]
        chat: Chat = Chat.objects.filter(
            chat_vk_id=event.peer_id
        )[0]
        chat_member: ChatMember = ChatMember.objects.filter(
            chat_member=kicked_member,
            chat=chat
        )[0]
        chat_member.delete()


class InviteUserCommand(BotCommand):
    """ команда добавления пользоателя """
    def __init__(self) -> None:
        super().__init__()

    def start(self, event: Event, **kwargs) -> Any:
        """ создание связи между новым пользователем и беседой """
        if not event.action_from_bot:
            try:
                new_member: Member = Member.objects.filter(
                    member_vk_id=event.action["member_id"]
                )[0]
            except IndexError:
                """ 
                если выброшена IndexError то пользователя с таким id 
                нет в бд. Значит пользователя нужно сохранить
                """
                member_response: UserResponse = UserResponse(self.api.users.get(event.action["member_id"]))
                new_member: Member = Member(
                    member_vk_id=member_response.id,
                    name=member_response.first_name,
                    surname=member_response.last_name
                ).save()
            finally:
                chat: Chat = Chat.objects.filter(
                    chat_vk_id=event.peer_id
                )[0]
                ChatMember(
                    chat=chat,
                    chat_member=new_member,
                    is_admin=False
                ).save()


class QueueEnrollCommand(BotCommand):
    """ команда записи в очередь """
    def __init__(self) -> None:
        super().__init__()
    
    def start(self, event: Event, **kwargs) -> Any:
        if event.button_type == "queue_enroll_button":
            queue: Queue = Queue.objects.filter(id=event.payload["queue_id"])[0]
            members: list[dict] = json.loads(queue.queue_members)
            members_ids = list(map(lambda member: member["member"], members))
            if event.from_id not in members_ids:
                members.append({
                    "member": event.from_id
                })
                queue.queue_members = json.dumps(members)
                queue.save()
