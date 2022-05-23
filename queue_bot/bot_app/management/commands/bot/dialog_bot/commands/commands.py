import json
from pprint import pprint
from typing import Any
from bot_app.management.commands.bot.bot_commands.command import BotCommand
from bot_app.management.commands.bot.bot_commands.commands_exceptions import MemberNotSavedError
from bot_app.management.commands.bot.dialog_bot.messages import QueueCreateMessages
from bot_app.management.commands.bot.middlewares.bot_api_middlewares import send_signal
from bot_app.management.commands.bot.vk_api.longpoll.responses import Event, UserResponse
from bot_app.models import Chat, ChatMember, Member, Queue, QueueChat
from bot_app.management.commands.bot.vk_api.keyboard.keyboard import Button, make_keyboard
from datetime import datetime
from bot_app.management.commands.bot.middlewares.keyboard_middlewares import chat_buttons, dialog_standart_buttons, days_buttons, yes_no_buttons
from bot_app.management.commands.bot.middlewares.middlewares import get_datetime, get_members, get_queue_day, get_start_time, get_time, members_saved
from bot_app.management.commands.bot.middlewares.db_middlewares import all_owner_chats, get_chat, queue_saved, is_owner


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
            message="функции бота",
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

        :event (Event) - событие с longpoll сервера
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
        """ 
        отправка сообщения о выборе беседы 
        
        """
        # полчение кнопок с беседами, где пользователь владелец
        chat_members: list[ChatMember] = all_owner_chats(user_id=event.from_id)
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
        if event.text == "да":
            members: list = get_members(
                peer_id=self.__queue_info[event.from_id]["chat"].chat_vk_id
            )
            queue: Queue = Queue(
                queue_name=self.__queue_info[event.from_id]["queue_name"],
                queue_members=json.dumps(members)
            )
            queue.save()
        elif event.text == "нет":
            queue: Queue = Queue(
                queue_name=self.__queue_info[event.from_id]["queue_name"],
                queue_members="[]"
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
        self.__current_step: dict = {}
    
    def start(self, event: Event, **kwargs) -> Any:
        super().start(event)
        if event.from_id not in self.__current_step:
            self.__current_step[event.from_id] = self.send_queues
        current_step_method = self.__current_step[event.from_id]
        current_step_method(event)

    def send_queues(self, event: Event) -> None:
        """ получение очередей, в которые может добавиться пользователь """
        chats: list[Chat] = list(map(  # список бесед, в которых есть пользователь
            lambda chat_member: chat_member.chat,
            ChatMember.objects.filter(chat_member=Member.objects.filter(member_vk_id=event.from_id)[0])
        ))
        queues: list[Queue] = []
        for chat in chats:
            queues.extend(list(map(
                lambda queue_chat: queue_chat.queue,
                QueueChat.objects.filter(chat=chat)
            )))
        if len(queues) == 0:
            self.api.messages.send(
                peer_id=event.peer_id,
                message="для вас нет очередей"
            )
            self.command_ended = True
        else:
            buttons = list(map(
                lambda queue: Button(label=queue.queue_name, payload={
                    "button_type": "queue_enroll_button",
                    "queue_id": queue.id
                }).button_json,
                queues
            ))
            self.api.messages.send(
                peer_id=event.peer_id,
                message="выберите очередь, в которую хотите записаться",
                keyboard=make_keyboard(
                    inline=False,
                    buttons=buttons[:40]
                )
            )
            self.__current_step[event.from_id] = self.get_queue
        
    def get_queue(self, event: Event) -> None:
        """ получение очереди из сообщения """
        if event.button_type == "queue_enroll_button":
            queue: Queue = Queue.objects.filter(id=event.payload["queue_id"])[0]
            members: list[dict] = json.loads(queue.queue_members)
            members_ids = list(map(lambda member: member["member"], members))
            if event.from_id not in members_ids:
                members.append({
                    "member": event.from_id
                })
                members_ids.append(event.from_id)
                queue.queue_members = json.dumps(members)
                queue.save()
                self.api.messages.send(
                    peer_id=event.peer_id,
                    message=(
                        "вы записались в очередь {0} из беседы {1}\n"
                        "ваш текущий номер - {2}"
                        .format(queue.queue_name, QueueChat.objects.filter(
                            queue=Queue.objects.filter(id=queue.id)[0])[0].chat,
                            members_ids.index(event.from_id)+1
                        )
                    ),
                    keyboard=make_keyboard(
                        inline=False,
                        buttons=[
                            Button(label="создать очередь").button_json,
                            Button(label="записаться в очередь").button_json,
                            Button(label="удалиться из очереди").button_json,
                            Button(label="получить место в очереди").button_json
                        ]
                    )
                )
            else:
                self.api.messages.send(
                    peer_id=event.peer_id,
                    message=(
                        "вы уже находитесь в этой очереди\n"
                        "ваш текущий порядковый номер - {0}".format(members_ids.index(event.from_id)+1)
                    ),
                    keyboard=make_keyboard(
                        inline=False,
                        buttons=[
                            Button(label="создать очередь").button_json,
                            Button(label="записаться в очередь").button_json,
                            Button(label="удалиться из очереди").button_json,
                            Button(label="получить место в очереди").button_json
                        ]
                    )
                )
            self.__current_step.pop(event.from_id)
            self.command_ended = True


class QueueQuitCommand(BotCommand):
    """ команда удаления из очереди """
    def __init__(self) -> None:
        super().__init__()
        self.__current_step: dict = {}
    
    def start(self, event: Event, **kwargs) -> Any:
        super().start(event)
        if event.from_id not in self.__current_step:
            self.__current_step[event.from_id] = self.send_queues
        current_step_method = self.__current_step[event.from_id]
        current_step_method(event)
        
    def send_queues(self, event: Event) -> None:
        queues: list[Queue] = []
        for queue in Queue.objects.all():
            members_ids = []
            queue_members = json.loads(queue.queue_members)
            if len(queue_members) > 0:
                members_ids = list(map(lambda member: member["member"], queue_members))
            if event.from_id in members_ids:
                queues.append(queue)
        buttons = list(map(
            lambda queue: Button(
                label=queue.queue_name,
                payload={
                    "button_type": "queue_delete_button",
                    "queue_id": queue.id
                }
            ).button_json,
            queues
        ))
        self.api.messages.send(
            peer_id=event.peer_id,
            message="выберите очередь из которой хотите удалиться",
            keyboard=make_keyboard(
                inline=False,
                buttons=buttons
            )
        )
        self.__current_step[event.from_id] = self.delete_member
    
    def delete_member(self, event: Event) -> None:
        if event.button_type == "queue_delete_button":
            queue: Queue = Queue.objects.filter(id=event.payload["queue_id"])[0]
            queue_members: list = json.loads(queue.queue_members)
            for member in queue_members:
                if member["member"] == event.from_id:
                    queue_members.remove(member)
            queue.queue_members = json.dumps(queue_members)
            queue.save()
        
        self.api.messages.send(
            peer_id=event.peer_id,
            message=(
                "вы удалились из очереди {0} в беседе {1}"
                .format(queue.queue_name, QueueChat.objects.filter(
                    queue=Queue.objects.filter(id=queue.id)[0])[0].chat
                )
            ),
            keyboard=make_keyboard(
                inline=False,
                buttons=[
                    Button(label="создать очередь").button_json,
                    Button(label="записаться в очередь").button_json,
                    Button(label="удалиться из очереди").button_json,
                    Button(label="получить место в очереди").button_json
                ]
            )
        )
    
        self.__current_step.pop(event.from_id)
        self.command_ended = True


class GetQueuePlaceCommand(BotCommand):
    """ команда получения места в очереди """
    def __init__(self) -> None:
        super().__init__()
        self.__current_step: dict = {}
    
    def start(self, event: Event, **kwargs) -> Any:
        super().start(event)
        if event.from_id not in self.__current_step:
            self.__current_step[event.from_id] = self.send_queues
        current_step_method = self.__current_step[event.from_id]
        current_step_method(event)

    def send_queues(self, event: Event) -> None:
        queues: list[Queue] = []
        for queue in Queue.objects.all():
            members_ids = []
            queue_members = json.loads(queue.queue_members)
            if len(queue_members) > 0:
                members_ids = list(map(lambda member: member["member"], queue_members))
            if event.from_id in members_ids:
                queues.append(queue)
        buttons = list(map(
            lambda queue: Button(
                label=queue.queue_name,
                payload={
                    "button_type": "queue_order_button",
                    "queue_id": queue.id
                }
            ).button_json,
            queues
        ))
        self.api.messages.send(
            peer_id=event.peer_id,
            message="выберите очередь",
            keyboard=make_keyboard(
                inline=False,
                buttons=buttons
            )
        )
        self.__current_step[event.from_id] = self.send_place

    def send_place(self, event: Event) -> None:
        if event.button_type == "queue_order_button":
            queue: Queue = Queue.objects.filter(id=event.payload["queue_id"])[0]
            members: list[dict] = json.loads(queue.queue_members)
            members_ids = list(map(lambda member: member["member"], members))
            users: list[str] = list(map(
                lambda member_id: "{index}. {name} {surname}".format(
                    index=members_ids.index(member_id) + 1,
                    name=UserResponse(self.api.users.get(member_id)).first_name,
                    surname=UserResponse(self.api.users.get(member_id)).last_name
                ),
                members_ids
            ))

            self.api.messages.send(
                peer_id=event.peer_id,
                message=(
                    "ваш номер в очереди - {0}".format(members_ids.index(event.from_id) + 1)
                )
            )
            self.api.messages.send(
                peer_id=event.peer_id,
                message=(
                    "\n".join(users)
                ),
                keyboard=make_keyboard(
                    inline=False,
                    buttons=[
                        Button(label="создать очередь").button_json,
                        Button(label="записаться в очередь").button_json,
                        Button(label="удалиться из очереди").button_json,
                        Button(label="получить место в очереди").button_json
                    ]
                )
            )
            self.__current_step.pop(event.from_id)
            self.command_ended = True
