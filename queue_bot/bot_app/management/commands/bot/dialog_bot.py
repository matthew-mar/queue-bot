from datetime import datetime
from pprint import pprint
import django
django.setup()

from .utils.bot_utils import read_token, VkApiMethods, week_days, get_days, get_datetime
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType
from .utils.keyboard.keyboard import make_keyboard
from ....models import ChatMember, Member, Chat, Queue, QueueChat


# авторизация
session: VkApi = VkApi(token=read_token())
api_methods: VkApiMethods = VkApiMethods(api=session.get_api())
current_command: dict = {}
queues: dict = {}


def is_owner(user_id: int, peer_id: int) -> bool:
    """
    определяет является ли пользвоатель владельцем беседы

    входные параметры:
    user_id (int): vk id пользователя

    peer_id (int): vk id чата, для отправления сообщения об ошибке

    выходные данные:
    True - если пользвоатель является владельцем
    False - если не является
    """
    try:
        # получение пользователя из бд по user_id
        user: Member = Member.objects.filter(member_vk_id=user_id)[0]
        # получение всех полей с пользователем, где он является админом беседы
        chats_members = ChatMember.objects.filter(
            chat_member=user,
            is_admin=True
        )
        # если длина QuerySet больше 0, то такие беседы есть, иначе нет
        return len(chats_members) > 0
    except IndexError:
        """
        если выбрасывается IndexError - то пользователя не существует в бд.
        """
        api_methods.messages.send(
            peer_id=peer_id,
            message="ошибка! вас нет в бд."
        )
        return False


def start_command(peer_id: int, user_id: int) -> None:
    """
    стартовая команда.

    определяет какой пользователь пишет боту - обычный или владелец беседы.

    в соответствии от типа пользвоателя отправляется соответствующее сообщение.

    входные параметры:
    peer_id (int): vk id чата, в котором происходит беседа
    """
    if is_owner(user_id=user_id, peer_id=peer_id):
        api_methods.messages.send(
            peer_id=peer_id,
            message="вы можете создать очередь для своей беседы",
            keyboard=make_keyboard(
                default_color="primary",
                buttons_names=["создать очередь"]
            )
        )
    else:
        api_methods.messages.send(
            peer_id=peer_id,
            message="для вас пока нет функций"
        )
        

def choose_chat(peer_id: int, user_id: int) -> None:
    """
    сообщение о выборе чата

    peer_id (int): vk id чата, в котором происходит общение

    user_id (int): vk id пользователя
    """
    if is_owner(user_id=user_id, peer_id=peer_id):
        chat_names: list[str] = [  # список чатов, в котором пользователь админ
            chat_member.chat.chat_name
            for chat_member in ChatMember.objects.filter(
                chat_member=Member.objects.filter(member_vk_id=user_id)[0],
                is_admin=True
            )
        ]
        api_methods.messages.send(
            peer_id=peer_id,
            message="выберите беседу, в которой будет очередь",
            keyboard=make_keyboard(
                default_color="primary",
                buttons_names=chat_names
            )
        )
        current_command[user_id] = "save_chat_name"


def save_chat_name(chat_name: str, user_id: int, peer_id: int) -> None:
    """
    функция сохраняет название чата в промежуточный словарь queues

    входные парметры:
    queue_name (str): название очереди

    user_id (int): vk id пользователя
    """
    queues[user_id] = {"chat_name": chat_name}

    api_methods.messages.send(
        peer_id=peer_id, 
        message="введите название очереди"
    )
    current_command[user_id] = "set_queue_name"


def set_queue_name(queue_name: str, user_id: int, peer_id: int) -> None:
    """
    сохраняет имя очереди
    """
    queues[user_id]["queue_name"] = queue_name

    api_methods.messages.send(
        peer_id=peer_id,
        message="введите день недели, в который начнется очередь",
        keyboard=make_keyboard(
            default_color="primary",
            buttons_names=get_days()
        )
    )
    current_command[user_id] = "choose_day"


def choose_day(week_day: str, user_id: int, peer_id: int) -> None:
    """
    функция сохраняет день недели во временный словарь, в который будет очередь

    входные параметры:
    day (str): номер дня недели от пользователя

    user_id (int): vk id пользователя, ключ временного словаря

    peer_id (int): vk id чата для отправки сообщения об ошибке
    """
    try:
        queues[user_id]["day"] = week_days[week_day]

        api_methods.messages.send(
            peer_id=peer_id,
            message="укажите время, когда начнет работать очередь\n"
                "формат ввода: hh:mm"
        )
        current_command[user_id] = "set_time"
    except KeyError:
        """
        если была выброшена KeyError, то пользователь не ввел название дня
        недели.
        """
        api_methods.messages.send(
            peer_id=peer_id,
            message="ошибка! введите правильно день недели",
            keyboard=make_keyboard(
                default_color="primary",
                buttons_names=list(week_days.keys())
            )
        )


def set_time(time_text: str, peer_id: int, user_id: int) -> None:
    try:
        hours, minutes = [
            int(i)
            for i in time_text.split(":")
        ]
        queues[user_id]["time"] = (hours, minutes)
        if hours > 23 or minutes > 60 or hours < 0 or minutes < 0:
            raise ValueError
        pprint(queues)
    except ValueError:
        api_methods.messages.send(
            peer_id=peer_id,
            message="ошибка! неверный формат данных"
        )
    
    save_queue(user_id=user_id)


def save_queue(user_id: int) -> None:
    """
    сохраняет очередь в бд
    """
    chat: Chat = Chat.objects.filter(chat_name=queues[user_id]["chat_name"])[0]
    queue_name: str = queues[user_id]["queue_name"]
    queue_datetime: datetime = get_datetime(
        day=queues[user_id]["day"],
        hours=queues[user_id]["time"][0],
        minutes=queues[user_id]["time"][1]
    )
    queue: Queue = Queue()
    queue.save()

    QueueChat(
        queue_datetime=queue_datetime,
        queue_name=queue_name,
        chat=chat,
        queue=queue
    ).save()


def command_handler(command: str, event) -> None:
    """
    обработчик команд

    входные параметры:
    command (str): текст команды
    
    event (DEFAULT_EVENT_CLASS): событие, требующее обработки
    """
    if command == "start_command":
        start_command(
            peer_id=event.peer_id, 
            user_id=event.user_id
        )
    
    if command == "choose_chat":
        choose_chat(
            peer_id=event.peer_id, 
            user_id=event.user_id
        )
    
    if command == "save_chat_name":
        save_chat_name(
            chat_name=event.text, 
            user_id=event.user_id,
            peer_id=event.peer_id
        )

    if command == "set_queue_name":
        set_queue_name(
            queue_name=event.text,
            user_id=event.user_id,
            peer_id=event.peer_id
        )
    
    if command == "choose_day":
        choose_day(
            week_day=event.text,
            user_id=event.user_id,
            peer_id=event.peer_id
        )

    if command == "set_time":
        set_time(
            user_id=event.user_id,
            peer_id=event.peer_id,
            time_text=event.text
        )


def run():
    longpoll: VkLongPoll = VkLongPoll(session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            message_text: str = event.text.lower()
            
            if event.to_me:
                if message_text == "начать":
                    current_command[event.user_id] = "start_command"

                if message_text == "создать очередь":
                    current_command[event.user_id] = "choose_chat"
            
                command_handler(
                    command=current_command.get(event.user_id), 
                    event=event
                )
