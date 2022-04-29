import django
django.setup()

from pprint import pprint
import requests
import vk
from bot_app.models import Member, Chat, ChatMember
from bot_app.management.commands.bot.utils.bot_utils import (
    read_token, VkApiMethods, week_days)
from bot_app.management.commands.bot.utils.keyboard.keyboard import (
    make_keyboard)


GROUP_ID: int = 206732640
VK_API_VERSION: float = 5.131
BOT_NAME: str = "[club206732640|@bboot]"

# авторизация
session: vk.Session = vk.Session(access_token=read_token())
api: vk.API = vk.API(session, v=VK_API_VERSION)
api_methods: VkApiMethods = VkApiMethods(api)


def is_group_add_message(message_text: str) -> bool:
    """
    функция возвращает True, если сообщение, которое пришло боту - это 
    приглашение в новою беседу.

    входные данные:
    message_text (str): функция принимает текст сообщения.

    когда бота добавляют в новую беседу, приходит пустое сообщение.

    выходные данные:
    функция возвращает результат сравнения длины текста сообщения с 0.
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
    2 - удачное сохранение беседы
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
        chat_name: str = chat_info["items"][0]["chat_settings"]["title"].lower()
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
            message="Ошибка! Сделайте бота администратором беседы.",
            keyboard=make_keyboard(one_time=True, **{
                "buttons_names": ["start"],
                "buttons_colors": ["positive"]
            })
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


def chat_members_connection(peer_id: int, profiles: list[dict], chat_info: dict) -> None:
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


def start_command(peer_id: int) -> bool:
    """
    функция стартовой команды.
    по этой команде функция пытается получить данные о беседе.
    если функции удается получить данные о беседе, то функция сохраняет беседу в бд
    затем сохраняет всех участников беседы в бд.
    затем устанвливает связь между беседами и её участниками в бд.
  
    входные данные:
    peer_id (int): id беседы.

    выходные данные:
    возвращает True - если удалось получить информацию о беседе и сохранить,
    иначе возвращает False.

    функция вызывается в двух режимах:
    1. Автоматически вызывается в цикле, который пробегается по всем беседам,
    куда добавили бота. После завершения команды, id беседы удаляется из списка.

    2. Вызывается через прямой запрос пользователя к боту.
    """
    print("\nstart command")
    # получение информации о беседе
    chat_info: dict = api_methods.messages.get_conversations_by_id(peer_id=peer_id)
    if chat_save(chat_info=chat_info, peer_id=peer_id) == 2:
        # получение информации об участниках беседы
        profiles: list[dict] = api_methods.messages.get_conversation_members(peer_id=peer_id)
        members_save(profiles=profiles)
        chat_members_connection(peer_id=peer_id, profiles=profiles, chat_info=chat_info)
        return True
    return False


def run() -> None:
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
            # если событие является сообщением
            if longpoll_updates[0]["object"].get("message"):
                # если получено новое сообщение
                if longpoll_updates[0]["type"] == "message_new":
                    # если сообщение из беседы
                    if longpoll_updates[0]["object"]["message"]["peer_id"] > 2000000000:
                            message_text: str = longpoll_updates[0]["object"]["message"]["text"].lstrip(BOT_NAME).lstrip(" ").lower()
                            if is_group_add_message(message_text=message_text):
                                print("добавление в новою беседу")
                                api_methods.messages.send(
                                    peer_id=longpoll_updates[0]["object"]["message"]["peer_id"],
                                    message="Здравствуйте! Чтобы пользоваться моими" 
                                        "функциями сделайте меня администратором беседы.\n"
                                        "Затем позовите меня с командой start",
                                    keyboard=make_keyboard(one_time=True, **{
                                        "buttons_names": ["start"],
                                        "buttons_colors": ["positive"]
                                    })
                                )

                            if message_text == "start":
                                if start_command(peer_id=longpoll_updates[0]["object"]["message"]["peer_id"]):
                                    api_methods.messages.send(
                                        peer_id=longpoll_updates[0]["object"]["message"]["peer_id"],
                                        message="Начало работы"
                                    )
                            
                            if message_text == "show days":
                                api_methods.messages.send(
                                    peer_id=longpoll_updates[0]["object"]["message"]["peer_id"],
                                    message="dfdsf",
                                    keyboard=make_keyboard(
                                        default_color="primary",
                                        buttons_names=list(week_days.keys())
                                    )
                                )

        # изменение ts для следующего запроса
        # ts - номер последнего события, начиная с которого нужно получать данные;
        ts = longpoll_response["ts"]
