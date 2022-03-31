import django
django.setup()

from pprint import pprint
import requests
import vk
from ....models import Member, Chat, ChatMember
from .bot_utils import read_token, VkApiMethods


def is_group_add_message(message_text: str) -> bool:
    """
    функция возвращает True, если сообщение, которое пришло боту - это 
    приглашение в новою беседу.

    входные данные:
    message_text (str): функция принимает текст сообщения.

    когда бота добавляют в новую беседу, приходит пустое сообщение.

    выходные данные:
    функция возвращает сравнение длины текста сообщения с 0.
    """
    return len(message_text) == 0


def chat_save(chat_info: dict, peer_id: int) -> int:
    """
    функция сохраняет беседу в бд.

    входные данные:
    chat_info (dict): информация о беседе из запроса.
    peer_id (int): id беседы для отправки сообщения об ошибке.

    выходные данные:
    1 - ошибка! беседа уже сохранена
    2 - удачное сохранение беседа
    3 - ошибка! бот не является администратором
    """
    print("\nпопытка сохранения беседы")
    
    chat_vk_ids: list[str] = [  # vk id бесед, сохраненных в бд
        int(chat.chat_vk_id)
        for chat in Chat.objects.all()
    ]
    if peer_id in chat_vk_ids:  # если id беседы находится в бд
        print("беседа уже сохранена")
        return 1

    try:
        # попытка инициализации полей модели Chat
        chat_name: str = chat_info["items"][0]["chat_settings"]["title"]
        chat_vk_id: int = peer_id

        # сохранение новой записи
        Chat(chat_vk_id=chat_vk_id, chat_name=chat_name).save()
        print(f"беседа {chat_name} сохранена")
        return 2
    except IndexError:
        """
        если выбрасывается IndexError, то бот не может получить доступ к данным
        о беседе, потому что не является администратором беседы.

        в этом случае выходим из функции с сообщением об ошибке.
        """
        print("не удалось сохранить беседу")
        api_methods.messages.send(
            peer_id=peer_id,
            message="Ошибка! Сделайте бота администратором беседы."
        )
        return 3


def members_save(profiles: list[dict]) -> None:
    """
    функция сохраняет участников беседы в бд.

    входные данные:
    profiles (list[dict]): список словарей с информацией о каждом пользователе.
    """
    print("\nсохранение участников беседы")

    # список vk id пользователей, сохраненных в бд
    members_vk_ids: list[int] = [
        int(member.member_vk_id)
        for member in Member.objects.all()
    ]
    for member in profiles:  # перебор участников беседы
        if member["id"] not in members_vk_ids:  # если пользователя нет в бд
            Member(  # сохранение пользователя в бд
                member_vk_id=member["id"],
                name=member["first_name"],
                surname=member["last_name"]
            ).save()
            print("пользователь {name} {surname} сохранен".format(
                name=member["first_name"],
                surname=member["last_name"]
            ))


def chat_members_connection(peer_id: int, profiles: list[dict], chat_info: dict):
    """
    сохранение в бд связи между беседой и участниками беседы.

    входные данные:
    peer_id (int): id беседы.
    profiles (list[dict]): список словарей с информацией о каждом участнике беседы.
    chat_info (dict): информация о беседе.
    """
    # получение беседы из бд
    chat: Chat = Chat.objects.filter(chat_vk_id=peer_id)[0]
    
    chats: list[Chat] = [
        chat_member.chat 
        for chat_member in ChatMember.objects.all()
    ]
    if chat not in chats:
        for member in profiles:
            # пробегаемся по каждому участнику беседы
            try:
                # получение участника беседы из бд по vk id
                chat_member: Member = Member.objects.filter(member_vk_id=member["id"])[0]
            except IndexError:
                """
                если была выброшена IndexError, то в бд нет пользователя с таким
                vk id, значит его нужно добавить в бд.
                """
                chat_member: Member = Member(
                    member_vk_id=member["id"],
                    name=member["first_name"],
                    surname=member["last_name"]
                ).save()
            # сохранение связи меджу беседой и участником беседы
            ChatMember(
                chat=chat,
                chat_member=chat_member,
                is_admin=(member["id"] == chat_info["items"][0]["chat_settings"]["owner_id"])
            ).save()


def start_command(peer_id: int):
    """
    функция стартовой команды срабатывает, когда пользователь пишет в беседе "start"
    по этой команде функция пытается получить данные о беседе.
    если функции удается получить данные о беседе, то функция сохраняет беседу в бд
    затем сохраняет всех участников беседы в бд.
    затем ставит флаг is_admin у владельца беседы.

    входные данные:
    peer_id (int): id беседы.
    """
    # получение информации о беседе
    chat_info: dict = api_methods.messages.get_conversations_by_id(peer_id=peer_id)
    if chat_save(chat_info=chat_info, peer_id=peer_id) == 2:
        # получение информации об участниках беседы
        profiles: list[dict] = api_methods.messages.get_conversation_members(peer_id=peer_id)
        members_save(profiles=profiles)

        chat_members_connection(peer_id=peer_id, profiles=profiles, chat_info=chat_info)


GROUP_ID: int = 206732640
VK_API_VERSION: float = 5.131

# авторизация
session: vk.Session = vk.Session(access_token=read_token())
api: vk.API = vk.API(session, v=VK_API_VERSION)
api_methods: VkApiMethods = VkApiMethods(api)


def start() -> None:
    # получение доступа к серверу
    longpoll_info: dict = api_methods.groups.get_longpoll_server(group_id=GROUP_ID)
    server, key, ts = longpoll_info["server"], longpoll_info["key"], longpoll_info["ts"]

    # прослушивание сервера
    while True:
        longpoll_response: dict = requests.post(server, data={  # получение ответа
            "act": "a_check",
            "key": key,
            "ts": ts,
            "wait": 25
        }).json()

        # получение списка событий от сервера
        longpoll_updates: list = longpoll_response["updates"]
        if longpoll_updates:  # если обновления есть
            # если получено новое сообщение
            if longpoll_updates[0]["type"] == "message_new":
                if is_group_add_message(longpoll_updates[0]["object"]["message"]["text"]):
                    print("добавление в новою беседу")
                    api_methods.messages.send(
                        peer_id=longpoll_updates[0]["object"]["message"]["peer_id"],
                        message="Здравствуйте! Чтобы пользоваться моими функциями сделайте меня администратором группы. Затем позовите меня и напишите start"
                    )
                else:
                    message_text: str = longpoll_updates[0]["object"]["message"]["text"].lstrip("[club206732640|bot] ").lower()
                    if message_text == "start":
                        print("\nкоманда start")
                        start_command(
                            peer_id=longpoll_updates[0]["object"]["message"]["peer_id"]
                        )
                        print("продолжение работы")

        # изменение ts для следующего запроса
        # ts - номер последнего события, начиная с которого нужно получать данные;
        ts = longpoll_response["ts"]
