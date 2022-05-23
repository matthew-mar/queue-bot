from datetime import datetime
from bot_app.management.commands.bot.bot_middlewares.vk_api_middlewares import get_chat_members
from bot_app.management.commands.bot.vk_api.longpoll.responses import MembersResponse
from bot_app.models import Member, ChatMember, Queue
import json


def get_week_day(day: int) -> str:
    """ 
    возвращает название дня недели по номеру
    
    :day (int) - номер дня недели
    """
    week_days = {
        0: "понедельник",
        1: "вторник",
        2: "среда",
        3: "четверг",
        4: "пятница",
        5: "суббота",
        6: "воскресенье"
    }

    return week_days[day]


def get_datetime(queue_info: dict) -> datetime:
    """
    формирование даты и времени из словаря с информацией об очереди

    :queue_info (dict)
    """
    return datetime(
        year=queue_info["date"]["year"],
        month=queue_info["date"]["month"],
        day=queue_info["date"]["day"],
        hour=queue_info["time"][0],
        minute=queue_info["time"][1]
    )


def get_queue_day(queue_datetime: datetime) -> str:
    """ 
    вовзвращает дату начала очереди в формате "dd.mm" 
    
    :queue_datetime (datetime) - дата начала очереди
    """
    return queue_datetime.strftime("%d.%m")


def get_start_time(time: tuple) -> str:
    """
    возвращает время начала очереди в формате "hh:mm"

    :time (tuple) - кортеж с данными о времени начала работы очереди
    """
    return "{0}:{1}".format(time[0], time[1])


def members_saved(queue_members: str) -> bool:
    """
    проверяет является ли список участников очереди пустым

    :queue_members (list) - список участников беседы
    """
    return len(json.loads(queue_members)) > 0


def get_time(time_string: str) -> tuple:
    """
    получает строку со временем в формате "hh:mm" и возвращает кортеж,
    где первый элемент - это часы, воторой - минуты
    
    :time_string (str) - время
    """
    time: tuple = tuple(map(int, time_string.split(":")))
    if time[0] > 23 or time[0] < 0 or time[1] > 60 or time[1] < 0:
        raise ValueError
    return time


def get_members(peer_id: int) -> list[dict[str:int]]:
    """
    функция возвращает список, состоящий из vk_id участников беседы в формате
    [{"member": vk_id}]

    :peer_id (int) - peer_id беседы
    """
    chat_members: MembersResponse = get_chat_members(peer_id)
    return list(map(
        lambda profile: {"member": profile.user_id},
        chat_members.profiles
    ))


def no_queues(queues: list[Queue]) -> bool:
    """
    принимает двумерный список с очередями и проверяет его на отсутствие очередей
    
    :queues (list[Queue]) - список с очередями
    """
    return sum(map(lambda queues_list: len(queues_list), queues)) == 0


def get_members_ids(queue_members: dict) -> list[int]:
    """
    вовзвращает список vk_id пользователей, находящихся в очереди
    """
    return list(map(
        lambda queue_member: queue_member["member"],
        json.loads(queue_members)
    ))


def member_in_queue(queue: Queue, user_id: int) -> bool:
    """
    проверяет является ли пользователь участником очереди

    :queue (Queue) - очередь
    :user_id (int) - vk_id пользователя
    """
    members_ids: list[int] = get_members_ids(queue_members=queue.queue_members)
    return user_id in members_ids


def get_member_order(queue: Queue, user_id: int) -> int:
    """
    вовзвращает порядковый номер участника очереди

    :queue (Queue) - очередь
    :user_id (int) - vk_id пользователя
    """
    members_ids: list[int] = get_members_ids(queue_members=queue.queue_members)
    return members_ids.index(user_id) + 1
