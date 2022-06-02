import json
from datetime import datetime
from bot_app.management.commands.bot.bot_middlewares.time_middlewares import dates_equal
from bot_app.management.commands.bot.bot_middlewares.vk_api_middlewares import get_user

from bot_app.management.commands.bot.vk_api.longpoll.responses import (
    ConversationsResponse, MembersResponse, Profile, UserResponse)

from bot_app.models import Member, Chat, Queue, QueueChat, ChatMember

from bot_app.management.commands.bot.bot_commands.commands_exceptions import (
    ChatAlreadySavedError, MemberNotSavedError, ChatDoesNotExistError, 
    NoChatMemberConnection, QueueChatDoesNotExistError, 
    QueueDoesNotExistError, QueueEmptyError)

from bot_app.management.commands.bot.bot_middlewares.vk_api_middlewares import (
    get_chat_members, get_user)


def get_member(vk_id: int) -> Member:
    """
    Возвращает участника беседы из бд по vk_id 
    
    :vk_id (int)
        vk_id пользователя.
    """
    try:
        return Member.objects.filter(member_vk_id=vk_id)[0]
    except IndexError:
        raise MemberNotSavedError


def get_chat(vk_id: int) -> Chat:
    """
    Возвращение беседы из бд по vk_id

    :vk_id (int)
        vk_id беседы.
    """
    try:
        return Chat.objects.filter(chat_vk_id=vk_id)[0]
    except IndexError:
        raise ChatDoesNotExistError


def get_chat_member(chat: Chat, chat_member: Member) -> ChatMember:
    """
    Получение связи "беседа-пользователь"

    :chat (Chat)
        объект беседы.
    
    :chat_member (Member)
        объект учатсника беседы.
    """
    try:
        return ChatMember.objects.filter(
            chat=chat,
            chat_member=chat_member
        )[0]
    except IndexError:
        raise NoChatMemberConnection


def get_queue_chat_by_queue(queue: Queue) -> QueueChat:
    """
    Возвращение связи "очередь-чат" из бд
    
    :queue (Queue)
        объект очереди.
    """
    try:
        return QueueChat.objects.filter(queue=queue)[0]
    except IndexError:
        raise QueueChatDoesNotExistError


def queue_saved(queue_name: str, queue_datetime: datetime, chat: Chat) -> bool:
    """ 
    Проверяет существует ли очередь в бд 
    
    :queue_name (str)
        название очереди.

    :queue_datetime (datetime)
        дата и время начала старта очереди.
    
    :chat (Chat)
        беседа, в которой находится очередь.
    """
    queues: list[Queue] = list(Queue.objects.filter(
        queue_name=queue_name
    ))
    for queue in queues:
        try:
            queue_chat: QueueChat = get_queue_chat_by_queue(queue=queue)
            dates: bool = dates_equal(date_1=queue_chat.queue_datetime, date_2=queue_datetime)
            chats: bool = queue_chat.chat == chat
            if dates and chats:  # если равны даты и беседы, такая очередь уже есть
                return True
        except QueueChatDoesNotExistError:
            continue
    return False


def is_owner(user_id: int) -> bool:
    """ 
    Проверка является ли пользователем владельцем беседы 
    
    :user_id (int)
        vk_id пользователя.
    """
    # список чатов, где пользователь является владельцем
    admin_chats: list[ChatMember] = all_owner_chat_members(user_id=user_id)
    return len(admin_chats) > 0


def all_chat_members(user_id: int) -> list:
    """
    Возвращает все связи "беседа-пользователь", где есть пользователь с user_id

    :user_id (int)
        vk_id пользователя.
    """
    return list(ChatMember.objects.filter(
        chat_member=get_member(vk_id=user_id)
    ))


def all_owner_chat_members(user_id: int) -> list[ChatMember]:
    """
    Список всех связей "беседа-пользователь", где пользователь является 
    владельцем беседы

    :user_id (int)
        vk_id пользователя.
    """
    return list(filter(
        lambda chat_member: chat_member.is_admin,
        all_chat_members(user_id=user_id)
    ))


def all_member_chats(user_id: int) -> list[Chat]:
    """
    Возвращает список всех бесед, где есть пользователь с user_id

    :user_id (int)
        vk_id пользователя. 
    """
    return list(map(
        lambda chat_member: chat_member.chat,
        all_chat_members(user_id=user_id)
    ))


def all_queues_chat(chat: Chat) -> list[QueueChat]:
    """
    Возвращает список всех связей "очередь-беседа", с определенной беседой

    :chat (Chat)
        объект беседы.
    """
    return list(QueueChat.objects.filter(chat=chat))


def all_queues_in_chat(peer_id: int) -> list[Queue]:
    """
    Вовзвращает список всех очередей в определенной беседе

    :peer_id (int)
        peer_id беседы.
    """
    return list(map(
        lambda queue_chat: queue_chat.queue,
        all_queues_chat(chat=get_chat(vk_id=peer_id))
    ))


def all_queues_in_member_chat(user_id: int) -> list[Queue]:
    """
    Возвращает список всех очередей с определенным пользователем

    :user_id (int)
        vk_id пользователя.
    """
    return list(map(
        lambda chat: all_queues_in_chat(peer_id=chat.chat_vk_id),
        all_member_chats(user_id=user_id)
    ))


def first_in_queue(queue_id: int):
    try:
        queue = get_queue_by_id(queue_id=queue_id)
        return get_members_ids(queue_members=queue.queue_members)[0]
    except IndexError:
        raise QueueEmptyError


def get_queue_by_id(queue_id: int) -> Queue:
    """
    Возвращает очередь по её id номеру из бд

    :queue_id (int)
        id номер очереди в бд.
    """
    try:
        return Queue.objects.filter(id=queue_id)[0]
    except IndexError:
        raise QueueDoesNotExistError


def queue_add_member(queue: Queue, user_id: int) -> None:
    """
    Добавление участника в очередь

    :queue (Queue)
        объект очереди.
    
    :user_id (int)
        vk_id пользователя.
    """
    queue_members: list[dict] = json.loads(queue.queue_members)
    if not member_in_queue(queue=queue, user_id=user_id):
        queue_members.append({"member": user_id})
        queue.queue_members = json.dumps(queue_members)
        queue.save()


def queue_delete_member(queue: Queue, user_id: int) -> None:
    """
    Удаление участника из очереди

    :queue (Queue)
        объект очереди.
    
    :user_id (int)
        vk_id пользователя.
    """
    queue_members: list[dict] = json.loads(queue.queue_members)
    try:
        member_index: int = get_member_order(queue=queue, user_id=user_id) - 1
        del queue_members[member_index]
        queue.queue_members = json.dumps(queue_members)
        queue.save()
    except ValueError:
        print(f"{user_id} нет в очереди")


def get_chat_by_queue(queue: Queue) -> Chat:
    """
    Возвращает беседу из связи "очередь-беседа" из бд по переданной очереди

    :queue (Queue)
        объект очереди.
    """
    return get_queue_chat_by_queue(queue).chat


def save_chat(conversation: ConversationsResponse) -> None:
    """
    Cохранение беседы в бд

    :peer_id (int)
        peer_id беседы.
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
    Функция сохраняет новый чат и возвращает его

    :conversation (ConversationResponse)
        информация о беседе.
    """
    save_chat(conversation=conversation)
    return get_chat(vk_id=conversation.peer_id)


def save_members(members_info: MembersResponse) -> None:
    """
    Функция сохраняет участников беседы в бд

    :members_info (MembersResponse)
        информация о пользователях.
    """
    # список id пользователей, сохраненных в бд
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
    Cохранение связи в бд между участниками беседы и беседой

    :chat (Chat)
        объект беседы.
    
    :profiles (list[Profile])
        список профилей участников беседы.
    
    :owner_id (int)
        vk_id владельца беседы.
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
    Cохранение беседы в бд

    :conversation (ConversationResponse)
        информация о беседе.
    
    :members (MembersResponse)
        информация об участниках беседы.
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
    Удаление связи между пользователем и беседой

    :member_id (int)
        vk_id пользователя.

    :chat_peer_id (int)
        peer_id беседы.
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
    Сохранение нового участника беседы 

    :member_id (int)
        vk_id пользователя.
    
    :chat_peer_id (int)
        peer_id беседы.
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


def get_week_day(day: int) -> str:
    """ 
    Возвращает название дня недели по номеру
    
    :day (int)
        номер дня недели.
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


def get_queue_day(queue_datetime: datetime) -> str:
    """ 
    Вовзвращает дату начала очереди в формате "dd.mm" 
    
    :queue_datetime (datetime)
        дата начала очереди.
    """
    return queue_datetime.strftime("%d.%m")


def get_start_time(queue_datetime: datetime) -> str:
    """
    Возвращает время начала очереди в формате "hh:mm"

    :time (tuple)
        кортеж с данными о времени начала работы очереди
    """
    return queue_datetime.strftime("%H:%M")


def members_saved(queue_members: str) -> bool:
    """
    Проверяет является ли список участников очереди пустым

    :queue_members (list)
        список участников беседы.
    """
    return len(json.loads(queue_members)) > 0


def get_members(peer_id: int) -> list[dict[str:int]]:
    """
    Функция возвращает список, состоящий из vk_id участников беседы в формате
    [{"member": vk_id}].

    :peer_id (int)
        peer_id беседы.
    """
    chat_members: MembersResponse = get_chat_members(peer_id)
    return list(map(
        lambda profile: {"member": profile.user_id},
        chat_members.profiles
    ))


def no_queues(queues: list[Queue]) -> bool:
    """
    Принимает двумерный список с очередями и проверяет его на отсутствие 
    очередей
    
    :queues (list[Queue])
        список с очередями.

    Если сумма длин строк двумерного списка равна 0, то двумерный список хранит
    пустые строки.
    """
    return sum(map(lambda queues_list: len(queues_list), queues)) == 0


def queues_empty(queues: list[Queue]) -> bool:
    """
    Проверка на пустой список очередей

    :queues (list[Queue])
        список очередей.
    """
    return len(queues) == 0


def get_members_ids(queue_members: str) -> list[int]:
    """
    Вовзвращает список vk_id пользователей, находящихся в очереди

    :queue_members (dict)
        json строка с участниками очереди.
    """
    return list(map(
        lambda queue_member: queue_member["member"],
        json.loads(queue_members)
    ))


def member_in_queue(queue: Queue, user_id: int) -> bool:
    """
    Проверяет является ли пользователь участником очереди

    :queue (Queue)
        объект очереди.
    
    :user_id (int)
        vk_id пользователя.
    """
    members_ids: list[int] = get_members_ids(queue_members=queue.queue_members)
    return user_id in members_ids


def get_member_order(queue: Queue, user_id: int) -> int:
    """
    Вовзвращает порядковый номер участника очереди

    :queue (Queue)
        объект очереди.
    
    :user_id (int)
        vk_id пользователя.
    """
    members_ids: list[int] = get_members_ids(queue_members=queue.queue_members)
    return members_ids.index(user_id) + 1


def get_queues_with_member(user_id: int) -> list[Queue]:
    """
    Возвращает только те очереди, где находится пользователь
    
    :user_id (int)
        vk_id пользователя.
    """
    queues = []
    queues_in_chats: list[Queue] = all_queues_in_member_chat(user_id)
    for queue_list in queues_in_chats:
        for queue in queue_list:
            if user_id in get_members_ids(queue_members=queue.queue_members):
                queues.append(queue)
    return queues


def get_queue_order(queue_members: str) -> str:
    """
    Возвращает порядок людей в очереди

    :queue_members (str)
        json строка с участниками очереди.
    """
    member_ids = get_members_ids(queue_members)
    users: list[str] = list(map(
        lambda member_id: "{index}. {name} {surname}".format(
            index=member_ids.index(member_id) + 1,
            name=get_user(member_id).first_name,
            surname=get_user(member_id).last_name
        ),
        member_ids
    ))
    return "\n".join(users)


def is_admin(conversation: ConversationsResponse) -> bool:
    """
    Проверка, является ли бот админом в беседе

    :conversation (ConversationsResponse)
        информация о беседе.

    если значение count = 1 - бот является админом
    """
    return conversation.count > 0

