import json
from pprint import pprint
from typing import Any
from bot_app.management.commands.bot.bot_commands.command import BotCommand
from bot_app.management.commands.bot.bot_commands.commands_exceptions import ChatAlreadySavedError, ChatBotIsNotAdminError, MemberNotSavedError
from bot_app.management.commands.bot.bot_middlewares.db_middlewares import connect_chat_with_members, delete_chat_member_connection, get_chat, get_chat_member, get_member, get_new_chat, get_queue_by_id, queue_add_member, save_chat, save_chat_member, save_members, save_new_member
from bot_app.management.commands.bot.bot_middlewares.middlewares import is_admin
from bot_app.management.commands.bot.bot_middlewares.vk_api_middlewares import get_chat_members, get_conversation, get_user
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
        super().start(event, **kwargs)

    def start_action(self, event: Event) -> None:
        """ удаление связи между пользователем и беседой """
        delete_chat_member_connection(
            member_id=event.action["member_id"],
            chat_peer_id=event.peer_id
        )
        self.end(event)


class InviteUserCommand(BotCommand):
    """ команда добавления пользоателя """
    def __init__(self) -> None:
        super().__init__()

    def start(self, event: Event, **kwargs) -> Any:
        return super().start(event, **kwargs)
    
    def start_action(self, event: Event) -> None:
        """ создание связи между новым пользователем и беседой """
        if not event.action_from_bot:
            save_new_member(
                member_id=event.action["member_id"], 
                chat_peer_id=event.peer_id
            )
        self.end(event)


class QueueEnrollCommand(BotCommand):
    """ команда записи в очередь """
    def __init__(self) -> None:
        super().__init__()

    def start(self, event: Event, **kwargs) -> Any:
        return super().start(event, **kwargs)

    def start_action(self, event: Event) -> None:
        if event.button_type == "queue_enroll_button":
            queue: Queue = get_queue_by_id(queue_id=event.payload["queue_id"])
            queue_add_member(queue=queue, user_id=event.from_id) 
        self.end(event)
