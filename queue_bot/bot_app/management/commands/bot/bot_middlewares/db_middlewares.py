import json
from typing import final
from bot_app.management.commands.bot.bot_middlewares.get_datetime import get_datetime
from bot_app.management.commands.bot.bot_middlewares.vk_api_middlewares import get_user
from bot_app.management.commands.bot.vk_api.longpoll.responses import ConversationsResponse, MembersResponse, Profile, UserResponse
from bot_app.models import Member, Chat, Queue, QueueChat, ChatMember
from bot_app.management.commands.bot.bot_commands.commands_exceptions import ChatAlreadySavedError, MemberNotSavedError, ChatDoesNotExistError, NoChatMemberConnection, QueueAlreadySaved, QueueDoesNotExistError
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


def get_chat_member(chat: Chat, chat_member: Member) -> ChatMember:
    """
    получение связи "беседа-пользователь"

    :chat (Chat) - объект беседы
    :chat_member (Member) - объект учатсника беседы
    """
    try:
        return ChatMember.objects.filter(
            chat=chat,
            chat_member=chat_member
        )[0]
    except IndexError:
        raise NoChatMemberConnection


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


def save_chat(conversation: ConversationsResponse) -> None:
    """
    сохранение беседы в бд

    :peer_id (int) - peer_id беседы
    """
    try:
        chat: Chat = get_chat(vk_id=conversation.peer_id)
        raise ChatAlreadySavedError(f"беседа {chat.chat_name} уже сохранена")
    except ChatDoesNotExistError:
        Chat(
            chat_name=conversation.title,
            chat_vk_id=conversation.peer_id
        ).save()


def get_new_chat(conversation: ConversationsResponse) -> Chat:
    """
    функция сохраняет новый чат и возвращает его

    :conversation (ConversationResponse) - информация о беседе
    """
    save_chat(conversation)
    return get_chat(vk_id=conversation.peer_id)


def save_members(members_info: MembersResponse) -> None:
    """
    функция сохраняет участников беседы в бд

    :members_info (MembersResponse) - информация о пользователях
    """
    # список пользователей, сохраненных в бд
    members_vk_ids: list[int] = list(map(
        lambda member: int(member.member_vk_id),
        Member.objects.all()
    ))
    for member in members_info.profiles:
        if member.user_id not in members_vk_ids:
            Member(
                member_vk_id=member.user_id,
                name=member.first_name,
                surname=member.last_name
            ).save()
            print("пользователь {name} {surname} сохранен".format(
                name=member.first_name,
                surname=member.last_name
            ))


def connect_chat_with_members(chat: Chat, profiles: list[Profile], owner_id: int) -> None:
    """
    сохранение связи в бд между участниками беседы и беседой

    :chat (Chat) - объект беседы
    :profiles (list[Profile]) - список профилей участников беседы
    :owner_id (int) - vk_id владельца беседы
    """
    members: list[Member] = list(map(  # получение участников беседы из бд
        lambda profile: get_member(vk_id=profile.user_id),
        profiles
    ))
    for member in members:
        ChatMember(
            chat=chat,
            chat_member=member,
            is_admin=(int(member.member_vk_id) == owner_id)
        ).save()


def save_chat_member(conversation: ConversationsResponse, members: MembersResponse) -> None:
    """
    сохранение беседы в бд

    :conversation (ConversationResponse) - информация о беседе
    :members (MembersResponse) - информация об участниках беседеы
    """
    chat: Chat = get_new_chat(conversation)
    save_members(members_info=members)
    connect_chat_with_members(
        chat=chat,
        profiles=members.profiles,
        owner_id=conversation.owner_id
    )


def delete_chat_member_connection(member_id: int, chat_peer_id: int) -> None:
    """
    удаление связи между пользователем и беседой

    :member_id (int) - vk_id пользователя
    :chat_peer_id (int) - peer_id беседы
    """
    kicked_member: Member = get_member(vk_id=member_id)
    chat: Chat = get_chat(vk_id=chat_peer_id)
    try:
        chat_member: ChatMember = get_chat_member(chat=chat, chat_member=kicked_member)
        chat_member.delete()
        print(f"{kicked_member.name} {kicked_member.surname} удален")
    except NoChatMemberConnection:
        print("пользователь не находился в беседе")


def save_new_member(member_id: int, chat_peer_id: int) -> None:
    """ 
    сохранение нового участника беседы 
    """
    try:
        new_member: Member = get_member(vk_id=member_id)
    except MemberNotSavedError:
        user: UserResponse = get_user(user_id=member_id)
        new_member: Member = Member(
            member_vk_id=user.id,
            name=user.first_name,
            surname=user.last_name
        ).save()
    finally:
        chat: Chat = get_chat(vk_id=chat_peer_id)
        ChatMember(
            chat=chat,
            chat_member=new_member,
            is_admin=False
        ).save()