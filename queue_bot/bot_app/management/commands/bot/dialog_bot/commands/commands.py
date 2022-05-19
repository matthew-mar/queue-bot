import json
from pprint import pprint
from typing import Any
from bot_app.bot_api.bot_api import BotApi
from bot_app.management.commands.bot.bot_commands.command import BotCommand
from bot_app.management.commands.bot.bot_commands.commands_exceptions import MemberNotSavedError, QueueAlreadySaved
from bot_app.management.commands.bot.vk_api.longpoll.responses import Event, MembersResponse, UsersResponse
from bot_app.models import Chat, ChatMember, Member, Queue, QueueChat
from bot_app.management.commands.bot.vk_api.keyboard.keyboard import Button, make_keyboard
from bot_app.management.commands.bot.vk_api.vk_api import Session
from datetime import datetime


def is_owner(event: Event) -> bool:
    """ проверка является ли пользователем владельцем беседы """
    api = Session().api
    user_response: dict = api.users.get(user_ids=event.from_id)
    user: UsersResponse = UsersResponse(user_response)
    try:
        member: Member = Member.objects.filter(member_vk_id=user.id)[0]
        # список чатов, где пользователь является владельцем
        admin_chats: list[ChatMember] = list(ChatMember.objects.filter(
            chat_member=member,
            is_admin=True
        ))
        return len(admin_chats) > 0
    except IndexError:
        """ 
        если выброшена IndexError, то пользователя нет в бд.
        это означает, что пользователя нет ни в одной беседе, где есть бот.
        """
        raise MemberNotSavedError()


class DialogStartCommand(BotCommand):
    """ начальная команда диалогового бота """
    def __init__(self) -> None:
        super().__init__()
    
    def start(self, event: Event, **kwargs) -> Any:
        """ 
        стартовая команда определяет какой пользователь пишет боту:
        обычный пользователь или владелец беседы
        """
        super().start(event)
        self.api.messages.send(
            peer_id=event.peer_id,
            message="функции бота",
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
        self.command_ended = True


class QueueCreateCommand(BotCommand):
    """ команда создания очереди """
    def __init__(self) -> None:
        super().__init__()
        # информация об очереди будет закрепляться за user.id 
        self.__queue_info: dict[int:dict] = {}
        # текущий шаг команды, ключом выступает user.id
        self.__current_step: dict = {}

    def start(self, event: Event, **kwargs) -> Any:
        super().start(event)
        try:
            if is_owner(event):
                if event.from_id not in self.__current_step:
                    self.__current_step[event.from_id] = self.choose_chat
                current_step_method = self.__current_step[event.from_id]
                current_step_method(event)
            else:
                self.api.messages.send(
                    peer_id=event.peer_id,
                    message=(
                        "чтобы создавать очереди нужно быть владельцем беседы, где есть бот"
                    )
                )
                self.command_ended = True
        except:
            self.api.messages.send(
                peer_id=event.peer_id,
                message=(
                    "чтобы пользоваться функциями бота нужно состоять в одной беседе с ботом"
                )
            )
            self.command_ended = True

    def choose_chat(self, event: Event) -> None:
        """ отправка сообщения о выборе беседы """
        if is_owner(event):
            chats: list[dict] = [  # список чатов, в которых пользователь админ
                Button(label=chat_member.chat.chat_name).button_json
                for chat_member in ChatMember.objects.filter(
                    chat_member=Member.objects.filter(member_vk_id=event.from_id)[0],
                    is_admin=True
                )
            ]
            self.api.messages.send(
                peer_id=event.peer_id,
                message="выберите беседу, в которой будет очередь",
                keyboard=make_keyboard(buttons=chats)
            )
        else:
            self.api.messages.send(
                peer_id=event.peer_id,
                message="вы не можете создавать очереди"
            )
        
        # переход к следующему шагу
        self.__current_step[event.from_id] = self.save_chat
    
    def save_chat(self, event: Event) -> None:
        """ сохранение названия чата """
        try:
            chat: Chat = Chat.objects.filter(chat_name=event.text)[0]
            self.__queue_info[event.from_id] = {"chat": chat}

            # переход к следующему шагу
            self.api.messages.send(
                peer_id=event.peer_id,
                message="введите название очереди"
            )
            self.__current_step[event.from_id] = self.save_queue_name
        except IndexError:
            """
            если выбрасывается IndexError, то пользователь ввел имя чата,
            которого нет в бд.
            """
            self.api.messages.send(
                peer_id=event.from_id,
                message="ошибка! вы не являетесь владельцем этой беседы"
            )
            return self.choose_chat(event)
    
    def save_queue_name(self, event: Event) -> None:
        """ сохранение названия беседы """
        queue_name: str = event.text.lower()
        self.__queue_info[event.from_id]["queue_name"] = queue_name

        days_buttons: list[dict] = list(map(
            lambda day: Button(label=day).button_json,
            self.__get_days()
        ))

        # переход к следующему шагу
        self.api.messages.send(
            peer_id=event.peer_id,
            message="введите день недели, когда начнет работать очередь",
            keyboard=make_keyboard(buttons=days_buttons)
        )
        self.__current_step[event.from_id] = self.save_day
    
    def save_day(self, event: Event) -> None:
        """ сохранения дня """
        week_days: dict[str:int] = {  # словарь соответствий дня недели с его номером
            "понедельник": 1,
            "вторник": 2,
            "среда": 3,
            "четверг": 4,
            "пятница": 5,
            "суббота": 6,
            "воскресенье": 7
        }

        try:
            self.__queue_info[event.from_id]["day"] = week_days[event.text]
            self.api.messages.send(
                peer_id=event.peer_id,
                message=(
                    "укажите время, когда начнет работать очередь\n"
                    "формат ввода: hh:mm"
                )
            )
            self.__current_step[event.from_id] = self.save_time
        except KeyError:
            """
            если была выброшена KeyError, то пользователь не ввел название дня
            недели.
            """
            days_buttons: list[dict] = list(map(
                lambda day: Button(label=day).button_json,
                self.__get_days()
            ))

            self.api.messages.send(
                peer_id=event.peer_id,
                message="ошибка! введите правильно день недели",
                keyboard=make_keyboard(buttons=days_buttons)
            )

    def save_time(self, event: Event) -> None:
        """ сохраняет введенное время """
        try:
            time = tuple(map(int, event.text.split(":")))
            if time[0] > 23 or time[1] > 60 or time[0] < 0 or time[1] < 0:
                raise ValueError
            self.__queue_info[event.from_id]["time"] = time

            self.api.messages.send(
                peer_id=event.peer_id,
                message=(
                    "Добавить участников беседы в очередь?\n"
                    "Да - участники беседы добавятся автоматически по порядку\n"
                    "Нет - участники беседы будут сами записываться в произвольном порядке"
                ),
                keyboard=make_keyboard(buttons=[
                    Button(label="да").button_json,
                    Button(label="нет").button_json
                ])
            )
            self.__current_step[event.from_id] = self.save_users
        except ValueError:
            return self.api.messages.send(
                peer_id=event.peer_id,
                message="ошибка! неверный формат данных"
            )

    def save_users(self, event: Event) -> None:
        """ сохранение пользователей """
        if event.text == "да":
            chat_members: dict = self.api.messages.get_conversation_members(
                peer_id=self.__queue_info[event.from_id]["chat"].chat_vk_id
            )
            members_response: MembersResponse = MembersResponse(chat_members)
            members: list = list(map(
                lambda profile: {"member": profile.user_id},
                members_response.profiles
            ))
            queue: Queue = Queue(
                queue_name=self.__queue_info[event.from_id]["queue_name"],
                queue_members=json.dumps(members))
            queue.save()
        elif event.text == "нет":
            queue: Queue = Queue(
                queue_name=self.__queue_info[event.from_id]["queue_name"],
                queue_members="[]"
            )
            queue.save()
        self.__queue_info[event.from_id]["queue"] = queue
        self.save_queue(event=event)
    
    def save_queue(self, event: Event) -> None:
        """ сохраняет очередь в бд """
        from datetime import datetime

        queue_info: dict = self.__queue_info[event.from_id]
        chat: Chat = queue_info["chat"]
        queue: Queue = queue_info["queue"]
        queue_datetime: datetime = self.__get_datetime(
            day=queue_info["day"],
            hours=queue_info["time"][0],
            minutes=queue_info["time"][1]
        )

        try:
            """
            проверка на существование очереди с введенными данными в бд.
            """
            # попытка получения очереди из бд
            queues: list[Queue] = list(Queue.objects.filter(queue_name=queue_info["queue"].queue_name))
            for queue in queues:
                try:
                    QueueChat.objects.filter(
                        queue_datetime=queue_datetime,
                        chat=chat,
                        queue=queue
                    )[0]
                    raise QueueAlreadySaved()
                except IndexError:
                    continue
            
            # сохранение связи между очередью и беседой
            QueueChat(
                queue_datetime=queue_datetime,
                chat=chat,
                queue=queue).save()

            self.api.messages.send(
                peer_id=event.peer_id,
                message="очередь успешно сохранена",
            )

            bot_api: BotApi = BotApi()
            data={
                "signal_name": "new_queue",
                "args": {
                    "chat_id": chat.chat_vk_id,
                    "queue_id": queue.id,
                    "queue_day": queue_datetime.strftime("%d.%m"),
                    "queue_start_time": "{hour}:{minutes}".format(
                        hour=queue_info["time"][0], 
                        minutes=queue_info["time"][1]),
                    "members_saved": not queue.queue_members == "[]"
                }
            }
            bot_api.send_signal(to="chat", data={"data": json.dumps(data)})
        except QueueAlreadySaved:
            queue_info["queue"].delete()
            self.api.messages.send(
                peer_id=event.peer_id,
                message="ошибка! такая очередь уже существует."
            )

        self.__queue_info.pop(event.from_id)
        self.__current_step.pop(event.from_id)
        self.command_ended = True

    def __get_days(self) -> list[str]:
        """ функция отправляет список доступных дней для пользователя """
        import datetime

        week_days: list[str] = {
            0: "понедельник",
            1: "вторник",
            2: "среда",
            3: "четверг",
            4: "пятница",
            5: "суббота",
            6: "воскресенье"
        }
        
        days: list[str] = []

        today: int = datetime.date.today().weekday()
        for day in week_days:
            if day >= today:
                days.append(week_days[day])
        return days
    
    def __get_datetime(self, day: int, hours: int, minutes: int) -> datetime:
        """ возвращает дату и время начала очереди """
        from week import Week

        months = {
            1: 31,
            2: 28,
            3: 31,
            4: 30,
            5: 31,
            6: 30,
            7: 31,
            8: 31,
            9: 30,
            10: 31,
            11: 30,
            12: 31
        }
        startdate = Week.thisweek().startdate
        original_month = int(startdate.strftime("%m"))
        days = int(startdate.strftime("%d")) + day - 1
        month = original_month + (days // months[original_month])
        days %= months[original_month] - 1

        return datetime(
            year=int(startdate.strftime("%Y")),
            month=month,
            day=days,
            hour=hours,
            minute=minutes
        )

    def queue_saved(self, user_id: int) -> bool:
        return user_id not in self.__current_step


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
                    name=UsersResponse(self.api.users.get(member_id)).first_name,
                    surname=UsersResponse(self.api.users.get(member_id)).last_name
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
