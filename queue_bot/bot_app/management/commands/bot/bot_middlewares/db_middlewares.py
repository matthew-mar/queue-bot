from bot_app.management.commands.bot.middlewares.middlewares import get_datetime
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


def all_owner_chats(user_id: int) -> bool:
    """
    список всех бесед, где пользователь является владельцем

    :user_id (int) - vk_id пользователя
    """
    return list(ChatMember.objects.filter(
        chat_member=get_member(vk_id=user_id),
        is_admin=True
    ))
