from bot_app.management.commands.bot.bot_commands.command import BotCommand
from bot_app.management.commands.bot.utils.bot_utils import (
    get_datetime, get_days)
from bot_app.management.commands.bot.utils.utils import is_owner
from bot_app.models import Chat, ChatMember, Member, QueueChat, Queue
from bot_app.management.commands.bot.utils.keyboard.keyboard import make_keyboard
from vk_api.longpoll import Event
from datetime import datetime


class QueueCreateCommand(BotCommand):
    """
    команда создания очередей
    """
    def __init__(self) -> None:
        super().__init__()

        # текущий шаг, ключом является id пользователя, значением является метод,
        # исполняющий определенную команду
        self.__current_step: dict = {}

        # словарь хранит информацию об очереди, ключом является event.user_id
        self.__queue_info: dict = {}

    def start(self, event: Event) -> str:
        if event.user_id not in self.__current_step:
            self.__current_step[event.user_id] = self.choose_chat
        return self.__current_step[event.user_id](event=event)
    
    def choose_chat(self, event: Event) -> str:
        """
        отправка сообщения о выборе беседы

        event: событие с VkLongPoll сервера
        """
        if is_owner(user_id=event.user_id, peer_id=event.peer_id):
            chat_names: list[str] = [  # список чатов, в котором пользователь админ
                chat_member.chat.chat_name
                for chat_member in ChatMember.objects.filter(
                    chat_member=Member.objects.filter(member_vk_id=event.user_id)[0],
                    is_admin=True
                )
            ]
            self.api.api.messages.send(
                peer_id=event.peer_id,
                message="выберите беседу, в которой будет очередь",
                keyboard=make_keyboard(
                    default_color="primary",
                    buttons_names=chat_names
                )
            )
            # переход к следующему шагу
            self.__current_step[event.user_id] = self.save_chat
            return "создать очередь"
        else:
            self.api.api.messages.send(
                peer_id=event.peer_id,
                message="вы не можете создавать очереди"
            )
            return "stop"

    def save_chat(self, event: Event) -> str:
        """
        функция сохраняет название чата в промежуточный словарь queues

        входные параметры:
        event: событие с VkLongPoll сервера
        """
        try:
            chat: Chat = Chat.objects.filter(chat_name=event.text)[0]
            self.__queue_info[event.user_id] = {"chat": chat}

            self.api.api.messages.send(
                peer_id=event.peer_id, 
                message="введите название очереди"
            )

            self.__current_step[event.user_id] = self.set_queue_name
        except IndexError:
            """
            если выбрасывается IndexError, то пользователь ввел имя чата,
            которого нет в бд.
            """
            chat_names: list[str] = [  # список чатов, в котором пользователь админ
                chat_member.chat.chat_name
                for chat_member in ChatMember.objects.filter(
                    chat_member=Member.objects.filter(member_vk_id=event.user_id)[0],
                    is_admin=True
                )
            ]
            self.api.api.messages.send(
                peer_id=event.peer_id,
                message="ошибка! вы не являетесь владельцем этой беседы\n"
                    "введите имя беседы из предложенного списка.",
                keyboard=make_keyboard(
                    default_color="primary",
                    buttons_names=chat_names
                )
            )
        return "создать очередь"
    
    def set_queue_name(self, event: Event) -> str:
        """
        сохраняет имя очереди

        входные параметры:
        event: событие с VkLongPoll сервера
        """
        self.__queue_info[event.user_id]["queue_name"] = event.text

        self.api.api.messages.send(
            peer_id=event.peer_id,
            message="введите день недели, в который начнется очередь",
            keyboard=make_keyboard(
                default_color="primary",
                buttons_names=get_days()
            )
        )

        self.__current_step[event.user_id] = self.choose_day
        return "создать очередь"
    
    def choose_day(self, event: Event) -> str:
        """
        функция сохраняет день недели во временный словарь, в который будет очередь
        
        входные параметры:
        event: событие с VkLongPoll сервера
        """
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
            self.__queue_info[event.user_id]["day"] = week_days[event.text]
            self.api.api.messages.send(
                peer_id=event.peer_id,
                message="укажите время, когда начнет работать очередь\n"
                    "формат ввода: hh:mm"
            )
            self.__current_step[event.user_id] = self.set_time
        except KeyError:
            """
            если была выброшена KeyError, то пользователь не ввел название дня
            недели.
            """
            self.api.api.messages.send(
                peer_id=event.peer_id,
                message="ошибка! введите правильно день недели",
                keyboard=make_keyboard(
                    default_color="primary",
                    buttons_names=get_days()
                )
            )
        return "создать очередь"
    
    def set_time(self, event: Event) -> str:
        """
        сохраняет введенное время для

        входные параметры:
        event: событие с VkLongPoll сервера
        """
        try:
            hours, minutes = [
                int(i)
                for i in event.text.split(":")
            ]
            self.__queue_info[event.user_id]["time"] = (hours, minutes)
            if hours > 23 or minutes > 60 or hours < 0 or minutes < 0:
                raise ValueError
        except ValueError:
            return self.api.api.messages.send(
                peer_id=event.peer_id,
                message="ошибка! неверный формат данных"
            )

        return self.save_queue(event=event)
    
    def save_queue(self, event: Event) -> str:
        """
        сохраняет очередь в бд

        входные параметры:
        event: событие с VkLongPoll сервера
        """

        queue_info: dict = self.__queue_info[event.user_id]
        chat: Chat = queue_info["chat"]
        queue_name: str = queue_info["queue_name"]
        queue_datetime: datetime = get_datetime(
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

            self.api.api.messages.send(
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

            self.api.api.messages.send(
                peer_id=event.peer_id,
                message="очередь успешно сохранена",
            )

        self.__queue_info.pop(event.user_id)
        self.__current_step.pop(event.user_id)
        return "stop"
