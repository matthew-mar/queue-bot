import json
from bot_app.management.commands.bot.bot_middlewares.get_datetime import get_datetime
from bot_app.models import Member, Chat, Queue, QueueChat, ChatMember
from bot_app.management.commands.bot.bot_commands.commands_exceptions import MemberNotSavedError, ChatDoesNotExistError, QueueAlreadySaved, QueueDoesNotExistError
from datetime import datetime


def get_member(vk_id: int) -> Member:
    """
    возвращение участника беседы из бд 
    
    :vk_id (int) - vk_id пользователя
    """
    try:
        return Member.objects.filter(member_vk_id=vk_id)[0]
    except IndexError:
        raise MemberNotSavedError


def get_chat(vk_id: int) -> Chat:
    """
    возвращение беседы из бд

    :vk_id (int) - vk_id беседы
    """
    try:
        return Chat.objects.filter(chat_vk_id=vk_id)[0]
    except IndexError:
        raise ChatDoesNotExistError


def get_queue_chat(queue_info: dict) -> Queue:
    """
    возвращение связи между чатом и очередью из бд
    
    :queue_info (dict) - данные об очереди
    """
    try:
        return QueueChat.objects.filter(
            queue_datetime=get_datetime(queue_info),
            chat=queue_info["chat"],
            queue=queue_info["queue"]
        )[0]
    except IndexError:
        raise QueueDoesNotExistError


def queue_saved(queue_info: dict) -> bool:
    """ 
    проверяет существует ли очередь в бд 
    
    :queue_info (dict) - словарь с набором параметров об очереди:
    беседа, название, дата и время, очередь
    """
    queues: list[Queue] = list(Queue.objects.filter(queue_name=queue_info["queue"].queue_name))
    for queue in queues:
        try:
            queue_chat = get_queue_chat(queue_info)
            return True
        except QueueDoesNotExistError:
            continue
    return False


def is_owner(user_id: int) -> bool:
    """ 
    проверка является ли пользователем владельцем беседы 
    
    :user_id (int) - vk_id пользователя
    """
    member: Member = get_member(vk_id=user_id)
    # список чатов, где пользователь является владельцем
    admin_chats: list[ChatMember] = list(ChatMember.objects.filter(
        chat_member=member,
        is_admin=True
    ))
    return len(admin_chats) > 0


def all_chat_members(user_id: int) -> list:
    """
    возвращает все связи "беседа-пользователь", где есть пользователь с user_id

    :user_id (int) - vk_id пользователя
    """
    return list(ChatMember.objects.filter(
        chat_member=get_member(vk_id=user_id)
    ))


def all_owner_chat_members(user_id: int) -> list:
    """
    список всех связей "беседа-пользователь", где пользователь является владельцем

    :user_id (int) - vk_id пользователя
    """
    return list(filter(
        lambda chat_member: chat_member.is_admin,
        all_chat_members(user_id)
    ))


def all_member_chats(user_id: int) -> list[Chat]:
    """
    возвращает список всех бесед, где есть пользователь

    :user_id (int) - vk_id пользователя 
    """
    return list(map(
        lambda chat_member: chat_member.chat,
        all_chat_members(user_id)
    ))


def all_queues_chat(chat: Chat) -> list[QueueChat]:
    """
    возвращает список всех связей "очередь-беседа", с определенной беседой

    :chat (Chat) - объект беседы
    """
    return list(QueueChat.objects.filter(chat=chat))


def all_queues_in_chat(chat: Chat) -> list[Queue]:
    """
    вовзвращает список всех очередей в определенной беседе

    :chat (Chat) - объект беседы
    """
    return list(map(
        lambda queue_chat: queue_chat.queue,
        all_queues_chat(chat)
    ))


def all_queues_in_member_chat(user_id: int) -> list[Queue]:
    """
    возвращает список всех очередей с определенным пользователем

    :user_id (int) - vk_id пользователя
    """
    return list(map(
        lambda chat: all_queues_in_chat(chat),
        all_member_chats(user_id)
    ))


def get_queue_by_id(queue_id: int) -> Queue:
    """
    возвращает очередь по её id номеру из бд

    :queue_id (int) - id номер очереди в бд
    """
    try:
        return Queue.objects.filter(id=queue_id)[0]
    except IndexError:
        raise QueueDoesNotExistError


def queue_add_member(queue: Queue, user_id: int) -> None:
    """
    добавление участника в очередь

    :queue (Queue) - объект очереди
    :user_id (int) - vk_id пользователя
    """
    queue_members: list[dict] = json.loads(queue.queue_members)
    queue_members.append({"member": user_id})
    queue.queue_members = json.dumps(queue_members)
    queue.save()


def queue_delete_member(queue: Queue, user_id: int) -> None:
    """
    удаление участника из очереди

    :queue (Queue) - объект очереди
    :user_id (int) - vk_id пользователя
    """
    queue_members: list[dict] = json.loads(queue.queue_members)
    for member in queue_members:
        if member["member"] == user_id:
            queue_members.remove(member)
            break
    queue.queue_members = json.dumps(queue_members)
    queue.save()


def get_queue_chat_by_queue(queue: Queue) -> QueueChat:
    """
    вовзвращает связь "очередь-беседа" из бд по переданной очереди

    :queue (Queue) - объект очереди
    """
    return QueueChat.objects.filter(queue=get_queue_by_id(queue_id=queue.id))[0]


def get_chat_by_queue(queue: Queue) -> Chat:
    """
    возвращает беседу из связи "очередь-беседа" из бд по переданной очереди

    :queue (Queue) - объект очереди
    """
    return get_queue_chat_by_queue(queue).chat
