from bot_app.management.commands.bot.bot_commands.command import BotCommand
from bot_app.management.commands.bot.bot_commands.commands_exceptions import ChatAlreadySavedError

from bot_app.management.commands.bot.bot_middlewares.db_middlewares import (
    all_queues_in_chat, all_queues_in_member_chat, delete_chat_member_connection, get_queue_by_id, get_queues_with_member, member_in_queue, queue_add_member, queue_delete_member,
    save_chat_member, save_new_member, is_admin)

from bot_app.management.commands.bot.bot_middlewares.vk_api_middlewares import (
    get_chat_members, get_conversation)

from bot_app.management.commands.bot.dialog_bot.messages import (
    ChatInvitationMessages, ChatStartMessages)

from bot_app.management.commands.bot.vk_api.longpoll.responses import (
    ConversationsResponse, Event, MembersResponse)

from bot_app.management.commands.bot.vk_api.keyboard.keyboard import Button, make_keyboard
from bot_app.models import Queue

from bot_app.management.commands.bot.bot_middlewares.bot_api_middlewares import send_signal


class ChatInvitationCommand(BotCommand):
    """ Команда приглашения в беседу """
    def __init__(self) -> None:
        super().__init__()
    
    def start(self, event: Event) -> None:
        super().start(event=event)
    
    def start_action(self, event: Event) -> None:
        self.api.messages.send(
            peer_id=event.peer_id,
            message=ChatInvitationMessages.START_MESSAGE,
            keyboard=make_keyboard(
                inline=False,
                buttons=[Button(label="start", color="positive").button_json]
            )
        )
        self.end(user_id=event.from_id)


class ChatStartCommand(BotCommand):
    """ Команда "start" в беседах """
    def __init__(self) -> None:
        super().__init__()

    def start(self, event: Event) -> None:
        super().start(event=event)

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
        self.end(user_id=event.from_id) 


class CickUserCommand(BotCommand):
    """ Команда удаления пользователя из беседы """
    def __init__(self) -> None:
        super().__init__()
    
    def start(self, event: Event) -> None:
        super().start(event=event)

    def start_action(self, event: Event) -> None:
        """ Удаление связи между пользователем и беседой """
        # удаление пользователя из всех очередей
        for queue in all_queues_in_chat(peer_id=event.peer_id):
            queue_delete_member(queue=queue, user_id=event.action["member_id"])

        delete_chat_member_connection(
            member_id=event.action["member_id"],
            chat_peer_id=event.peer_id
        )
        self.end(user_id=event.from_id)


class InviteUserCommand(BotCommand):
    """ Команда добавления пользоателя """
    def __init__(self) -> None:
        super().__init__()

    def start(self, event: Event) -> None:
        return super().start(event)
    
    def start_action(self, event: Event) -> None:
        """ создание связи между новым пользователем и беседой """
        if not event.action_from_bot:
            save_new_member(
                member_id=event.action["member_id"], 
                chat_peer_id=event.peer_id
            )
        self.end(user_id=event.from_id)


class QueueEnrollCommand(BotCommand):
    """ команда записи в очередь """
    def __init__(self) -> None:
        super().__init__()

    def start(self, event: Event) -> None:
        return super().start(event=event)

    def start_action(self, event: Event) -> None:
        if event.button_type == "queue_enroll_button":
            queue: Queue = get_queue_by_id(queue_id=event.payload["queue_id"])
            signal_data = {
                "signal_name": "queue_enroll_from_chat",
                "args": {
                    "user_id": event.from_id,
                    "queue_id": event.payload["queue_id"],
                    "member_in_queue": member_in_queue(queue=queue, user_id=event.from_id)
                }
            }
            queue_add_member(queue=queue, user_id=event.from_id) 
            send_signal(to="dialog", data=signal_data)
        self.end(user_id=event.from_id)
