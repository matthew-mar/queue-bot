from asyncio import events
from typing import Any
from bot_app.management.commands.bot.bot_commands.command import BotCommand
from bot_app.management.commands.bot.bot_commands.commands_exceptions import MemberNotSavedError
from bot_app.management.commands.bot.utils.server.responses import Event, UsersResponse
from bot_app.models import Chat, ChatMember, Member, Queue, QueueChat
from bot_app.management.commands.bot.utils.keyboard.keyboard import make_keyboard
from bot_app.management.commands.bot.utils.api import Session
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
        try:
            if is_owner(event):
                self.api.messages.send(
                    peer_id=event.peer_id,
                    message="вы можете создать очередь",
                    keyboard=make_keyboard(
                        buttons_names=["создать очередь"]
                    )
                )
            else:
                self.api.messages.send(
                    peer_id=event.peer_id,
                    message="для вас пока нет функций"
                )
        except MemberNotSavedError:
            self.api.messages.send(
                peer_id=event.peer_id,
                message=(
                    "чтобы пользоваться функциями бота нужно быть владельцем "
                    "или участником беседы, куда добавлен бот"
                )
            )


class QueueCreateCommand(BotCommand):
    """ команда создания очереди """
    def __init__(self) -> None:
        super().__init__()
        # информация об очереди будет закрепляться за user.id 
        self.__queue_info: dict[int:dict] = {}
        # текущий шаг команды, ключом выступает user.id
        self.__current_step: dict = {}

    def start(self, event: Event, **kwargs) -> Any:
        if event.from_id not in self.__current_step:
            self.__current_step[event.from_id] = self.choose_chat
        current_step_method = self.__current_step[event.from_id]
        current_step_method(event)

    def choose_chat(self, event: Event) -> None:
        """ отправка сообщения о выборе беседы """
        if is_owner(event):
            chats: list[str] = [  # список чатов, в которых пользователь админ
                chat_member.chat.chat_name
                for chat_member in ChatMember.objects.filter(
                    chat_member=Member.objects.filter(member_vk_id=event.from_id)[0],
                    is_admin=True
                )
            ]
            self.api.messages.send(
                peer_id=event.peer_id,
                message="выберите беседу, в которой будет очередь",
                keyboard=make_keyboard(
                    default_color="primary",
                    buttons_names=chats
                )
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

        # переход к следующему шагу
        self.api.messages.send(
            peer_id=event.peer_id,
            message="введите день недели, когда начнет работать очередь",
            keyboard=make_keyboard(
                default_color="primary",
                buttons_names=self.__get_days()
            )
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
            self.api.messages.send(
                peer_id=event.peer_id,
                message="ошибка! введите правильно день недели",
                keyboard=make_keyboard(
                    default_color="primary",
                    buttons_names=self.__get_days()
                )
            )

    def save_time(self, event: Event) -> None:
        """ сохраняет введенное время """
        try:
            time = tuple(map(int, event.text.split(":")))
            if time[0] > 23 or time[1] > 60 or time[0] < 0 or time[1] < 0:
                raise ValueError
            self.__queue_info[event.from_id]["time"] = time
            self.save_queue(event)
        except ValueError:
            return self.api.messages.send(
                peer_id=event.peer_id,
                message="ошибка! неверный формат данных"
            )
    
    def save_queue(self, event: Event) -> None:
        """ сохраняет очередь в бд """
        from datetime import datetime

        queue_info: dict = self.__queue_info[event.from_id]
        chat: Chat = queue_info["chat"]
        queue_name: str = queue_info["queue_name"]
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
            QueueChat.objects.filter(
                chat=chat,
                queue_name=queue_name,
                queue_datetime=queue_datetime)[0]

            self.api.messages.send(
                peer_id=event.peer_id,
                message="ошибка! такая очередь уже существует."
            )
        except IndexError:
            """
            если выбрасывается IndexError, значит такой очереди нет в бд.
            """

            # сохранение нового объекта очереди
            queue: Queue = Queue()
            queue.save()

            # сохранение связи между очередью и беседой
            QueueChat(
                queue_datetime=queue_datetime,
                queue_name=queue_name,
                chat=chat,
                queue=queue).save()

            self.api.messages.send(
                peer_id=event.peer_id,
                message="очередь успешно сохранена",
            )

            self.__queue_info.pop(event.from_id)
            self.__current_step.pop(event.from_id)

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
