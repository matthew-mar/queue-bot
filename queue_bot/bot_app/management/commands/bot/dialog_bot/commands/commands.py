import json
from pprint import pprint
from typing import Any
from bot_app.management.commands.bot.bot_commands.command import BotCommand
from bot_app.management.commands.bot.bot_commands.commands_exceptions import MemberNotSavedError
from bot_app.management.commands.bot.dialog_bot.messages import DialogStartMessages, GetQueuePlaceMessages, QueueCreateMessages, QueueEnrollMessages, QueueQuitMessages
from bot_app.management.commands.bot.bot_middlewares.bot_api_middlewares import send_signal
from bot_app.management.commands.bot.vk_api.longpoll.responses import Event, UserResponse
from bot_app.models import Chat, ChatMember, Member, Queue, QueueChat
from bot_app.management.commands.bot.vk_api.keyboard.keyboard import Button, make_keyboard
from datetime import datetime
from bot_app.management.commands.bot.bot_middlewares.keyboard_middlewares import chat_buttons, dialog_standart_buttons, days_buttons, queues_buttons, queues_delete_buttons, queues_order_buttons, yes_no_buttons
from bot_app.management.commands.bot.bot_middlewares.middlewares import get_member_order, get_members, get_queue_day, get_queue_order, get_queues_with_member, get_start_time, get_time, members_saved, no_queues, member_in_queue, queues_empty
from bot_app.management.commands.bot.bot_middlewares.db_middlewares import all_member_chats, all_owner_chat_members, all_queues_in_member_chat, get_chat, get_chat_by_queue, get_queue_by_id, queue_add_member, queue_delete_member, queue_saved, is_owner
from bot_app.management.commands.bot.bot_middlewares.get_datetime import get_datetime


class DialogStartCommand(BotCommand):
    """ начальная команда диалогового бота """
    def __init__(self) -> None:
        super().__init__()
    
    def start(self, event: Event, **kwargs) -> Any:
        super().start(event)
    
    def start_action(self, event: Event) -> None:
        """
        стартовая команда предоставляет пользователю функционал бота
        """
        self.api.messages.send(
            peer_id=event.peer_id,
            message=DialogStartMessages.MESSAGE,
            keyboard=make_keyboard(
                inline=False,
                buttons=dialog_standart_buttons
            )
        )
        self.end(event)


class QueueCreateCommand(BotCommand):
    """ команда создания очереди """
    def __init__(self) -> None:
        super().__init__()
        # информация об очереди будет закрепляться за user.id 
        self.__queue_info: dict[int:dict] = {}

    def start(self, event: Event, **kwargs) -> Any:
        super().start(event)
    
    def start_action(self, event: Event) -> None:
        """
        начальное действие команды определяет какой пользователь пишет боту.
        если пользователь является владельцем беседы - команда идет дальше.
        если пользователь не является владельцем беседы - команда завершается.
        если пользователя нет в бд - команда завершается.
        """
        try:
            if is_owner(user_id=event.from_id):
                self.go_next(
                    event=event,
                    next_method=self.choose_chat,
                    next_step=self.save_chat
                )
            else:
                self.api.messages.send(
                    peer_id=event.peer_id,
                    message=QueueCreateMessages.NOT_OWNER_MESSAGE
                )
                self.end(event)
        except MemberNotSavedError:
            self.api.messages.send(
                peer_id=event.peer_id,
                message=QueueCreateMessages.MEMBER_NOT_SAVED_MESSAGE
            )
            self.end(event)

    def choose_chat(self, event: Event) -> None:
        """ отправка сообщения о выборе беседы """
        # полчение кнопок с беседами, где пользователь владелец
        chat_members: list[ChatMember] = all_owner_chat_members(user_id=event.from_id)
        self.api.messages.send(
            peer_id=event.peer_id,
            message=QueueCreateMessages.CHOOSE_CHAT_MESSAGE,
            keyboard=make_keyboard(buttons=chat_buttons(chat_members))
        )

    def choose_queue_name(self, event: Event) -> None:
        """ отправка сообщения о имени очереди """
        self.api.messages.send(
            peer_id=event.peer_id,
            message=QueueCreateMessages.QUEUE_NAME_ENTER_MESSAGE
        )

    def choose_day(self, event: Event) -> None:
        """ отправка сообщения о выборе дня """
        self.api.messages.send(
            peer_id=event.peer_id,
            message=QueueCreateMessages.DAY_ENTER_MESSAGE,
            keyboard=make_keyboard(buttons=days_buttons())
        )

    def choose_time(self, event: Event) -> None:
        """ отправка сообщения о выборе времени """
        self.api.messages.send(
            peer_id=event.peer_id,
            message=QueueCreateMessages.TIME_ENTER_MESSAGE
        )
    
    def choose_members_saving(self, event: Event) -> None:
        """ отправка сообщения о выборе сохранения участников беседы в очередь """
        self.api.messages.send(
            peer_id=event.peer_id,
            message=QueueCreateMessages.MEMBERS_ADD_MESSAGE,
            keyboard=make_keyboard(buttons=yes_no_buttons)
        )
    
    def save_chat(self, event: Event) -> None:
        """ сохранение чата """
        if event.button_type == "chat_name_button":
            chat: Chat = get_chat(vk_id=event.payload["chat_id"])
            self.__queue_info[event.from_id] = {"chat": chat}

            self.go_next(
                event=event,
                next_method=self.choose_queue_name,
                next_step=self.save_queue_name
            )
        else:
            self.api.messages.send(
                peer_id=event.from_id,
                message=QueueCreateMessages.OWNER_ERROR_MESSAGE
            )
            return self.choose_chat(event)
    
    def save_queue_name(self, event: Event) -> None:
        """ сохранение названия беседы """
        queue_name: str = event.text.lower()
        self.__queue_info[event.from_id]["queue_name"] = queue_name

        self.go_next(
            event=event,
            next_method=self.choose_day,
            next_step=self.save_day
        )
    
    def save_day(self, event: Event) -> None:
        """ сохранения дня """
        if event.button_type == "week_day":
            self.__queue_info[event.from_id]["date"] = event.payload["date"]
            
            self.go_next(
                event=event,
                next_method=self.choose_time,
                next_step=self.save_time
            )
        else:
            self.api.messages.send(
                peer_id=event.peer_id,
                message=QueueCreateMessages.DAY_ERROR_MESSAGE,
                keyboard=make_keyboard(buttons=days_buttons())
            )

    def save_time(self, event: Event) -> None:
        """ сохраняет введенное время """
        try:
            self.__queue_info[event.from_id]["time"] = get_time(time_string=event.text)

            self.go_next(
                event=event,
                next_method=self.choose_members_saving,
                next_step=self.save_users
            )
        except ValueError:
            return self.api.messages.send(
                peer_id=event.peer_id,
                message=QueueCreateMessages.TIME_FORMAT_ERROR
            )
            
    def save_users(self, event: Event) -> None:
        """ сохранение пользователей """
        if event.text in ("да", "нет"):
            if event.text == "да":
                members: list = get_members(
                    peer_id=self.__queue_info[event.from_id]["chat"].chat_vk_id
                )
            elif event.text == "нет":
                members: list = []
            queue: Queue = Queue(
                queue_name=self.__queue_info[event.from_id]["queue_name"],
                queue_members=json.dumps(members)
            )
            queue.save()
        else:
            return self.api.messages.send(
                peer_id=event.peer_id,
                message=QueueCreateMessages.YES_NO_ERROR_MESSAGE,
                keyboard=make_keyboard(buttons=yes_no_buttons)
            )

        self.__queue_info[event.from_id]["queue"] = queue
        self.save_queue(event=event)
    
    def save_queue(self, event: Event) -> None:
        """ сохраняет очередь в бд """
        queue_info: dict = self.__queue_info[event.from_id]
        chat: Chat = queue_info["chat"]
        queue: Queue = queue_info["queue"]
        queue_datetime: datetime = get_datetime(queue_info)

        if queue_saved(queue_info):  # если такая очередь сохранена
            queue_info["queue"].delete()
            self.api.messages.send(
                peer_id=event.peer_id,
                message=QueueCreateMessages.QUEUE_ALREADY_SAVED_MESSAGE
            )
        else:
            # сохранение связи между очередью и беседой
            QueueChat(
                queue_datetime=queue_datetime,
                chat=chat,
                queue=queue).save()
            self.api.messages.send(
                peer_id=event.peer_id,
                message=QueueCreateMessages.QUEUE_SUCCESSFULLY_SAVED_MESSAGE,
            )

            send_signal(  # отправить сигнал чат боту о появлении новой очереди
                to="chat",
                data={
                    "signal_name": "new_queue",
                    "args": {
                        "chat_id": chat.chat_vk_id,
                        "queue_id": queue.id,
                        "queue_day": get_queue_day(queue_datetime),
                        "queue_start_time": get_start_time(time=queue_info["time"]),
                        "members_saved": members_saved(queue_members=queue.queue_members)
                    }
                }
            )

        self.__queue_info.pop(event.from_id)
        self.end(event)


class QueueEnrollCommand(BotCommand):
    """ команда записи в очередь """
    def __init__(self) -> None:
        super().__init__()
    
    def start(self, event: Event, **kwargs) -> Any:
        super().start(event)
    
    def start_action(self, event: Event) -> None:
        """ 
        в начальном действии команда отправляет очереди, 
        в которые можно записаться 
        """
        self.go_next(
            event=event,
            next_method=self.send_queues,
            next_step=self.get_queue
        )

    def send_queues(self, event: Event) -> None:
        """ отправка очередей, в которые может добавиться пользователь """
        queues: list[list[Queue]] = all_queues_in_member_chat(user_id=event.from_id)
        if no_queues(queues):
            self.api.messages.send(
                peer_id=event.peer_id,
                message=QueueEnrollMessages.NO_QUEUES_MESSAGE
            )
            self.end(event)
        else:
            self.api.messages.send(
                peer_id=event.peer_id,
                message=QueueEnrollMessages.CHOOSE_QUEUE_MESSAGE,
                keyboard=make_keyboard(buttons=queues_buttons(queues))
            )
        
    def get_queue(self, event: Event) -> None:
        """ получение очереди из сообщения """
        if event.button_type == "queue_enroll_button":
            queue: Queue = get_queue_by_id(queue_id=event.payload["queue_id"])
            if member_in_queue(queue=queue, user_id=event.from_id):
                message=QueueEnrollMessages.ALREADY_IN_QUEUE_MESSAGE.format(
                    get_member_order(
                        queue=queue,
                        user_id=event.from_id
                    )
                )
            else:
                queue_add_member(queue=queue, user_id=event.from_id)
                message=QueueEnrollMessages.QUEUE_ENROLLED_MESSAGE.format(
                    queue.queue_name, 
                    get_chat_by_queue(queue),
                    get_member_order(queue=queue, user_id=event.from_id)
                )
            
            self.api.messages.send(
                peer_id=event.peer_id,
                message=message,
                keyboard=make_keyboard(
                    inline=False,
                    buttons=dialog_standart_buttons
                )
            )
            self.end(event)
        else:
            self.api.messages.send(
                peer_id=event.peer_id,
                message=QueueEnrollMessages.QUEUE_ENROLL_ERROR_MESSAGE
            )
            self.send_queues(event)


class QueueQuitCommand(BotCommand):
    """ команда удаления из очереди """
    def __init__(self) -> None:
        super().__init__()
    
    def start(self, event: Event, **kwargs) -> Any:
        super().start(event)

    def start_action(self, event: Event) -> None:
        self.go_next(
            event=event,
            next_method=self.send_queues,
            next_step=self.delete_member
        )
        
    def send_queues(self, event: Event) -> None:
        queues: list[Queue] = get_queues_with_member(user_id=event.from_id)
        if queues_empty(queues):
            self.api.messages.send(
                peer_id=event.peer_id,
                message=QueueQuitMessages.NOT_IN_ANY_QUEUE_MESSAGE,
                keyboard=make_keyboard(
                    inline=False,
                    buttons=dialog_standart_buttons
                )
            )
            self.end(event)
        else:
            self.api.messages.send(
                peer_id=event.peer_id,
                message=QueueQuitMessages.CHOOSE_QUEUE_MESSAGE,
                keyboard=make_keyboard(buttons=queues_delete_buttons(queues))
            )
    
    def delete_member(self, event: Event) -> None:
        if event.button_type == "queue_delete_button":
            queue: Queue = get_queue_by_id(queue_id=event.payload["queue_id"])
            queue_delete_member(queue=queue, user_id=event.from_id)
        
            self.api.messages.send(
                peer_id=event.peer_id,
                message=(
                    QueueQuitMessages.ON_QUIT_MESSAGE
                    .format(queue.queue_name, get_chat_by_queue(queue))
                ),
                keyboard=make_keyboard(
                    inline=False,
                    buttons=dialog_standart_buttons
                )
            )

            self.end(event)
        else:
            self.api.messages.send(
                peer_id=event.peer_id,
                message=QueueQuitMessages.QUEUE_ERROR_MESSAGE
            )
            self.send_queues(event)


class GetQueuePlaceCommand(BotCommand):
    """ команда получения места в очереди """
    def __init__(self) -> None:
        super().__init__()
    
    def start(self, event: Event, **kwargs) -> Any:
        super().start(event)

    def start_action(self, event: Event) -> None:
        self.go_next(
            event=event,
            next_method=self.send_queues,
            next_step=self.send_place
        )

    def send_queues(self, event: Event) -> None:
        queues: list[Queue] = get_queues_with_member(user_id=event.from_id)
        if queues_empty(queues):
            self.api.messages.send(
                peer_id=event.peer_id,
                message=QueueQuitMessages.NOT_IN_ANY_QUEUE_MESSAGE,
                keyboard=make_keyboard(
                    inline=False,
                    buttons=dialog_standart_buttons
                )
            )
            self.end(event)
        else:
            self.api.messages.send(
                peer_id=event.peer_id,
                message=GetQueuePlaceMessages.CHOOSE_QUEUE_MESSAGE,
                keyboard=make_keyboard(
                    inline=True,
                    buttons=queues_order_buttons(queues)
                )
            )            

    def send_place(self, event: Event) -> None:
        if event.button_type == "queue_order_button":
            queue: Queue = get_queue_by_id(queue_id=event.payload["queue_id"])

            self.api.messages.send(
                peer_id=event.peer_id,
                message=(
                    GetQueuePlaceMessages.QUEUE_ORDER_MESSAGE.format(
                        get_member_order(queue=queue, user_id=event.from_id),
                        get_queue_order(queue.queue_members)
                    )
                ),
                keyboard=make_keyboard(
                    inline=False,
                    buttons=dialog_standart_buttons
                )
            )
            self.end(event)
