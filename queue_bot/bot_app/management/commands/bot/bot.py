import django
django.setup()

from pprint import pprint
import requests
import vk
from ....models import Member, Chat
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
    chat_vk_ids: list[str] = [  # vk id бесед, сохраненных в бд
        int(chat.chat_vk_id)
        for chat in Chat.objects.all()
    ]
    if peer_id in chat_vk_ids:  # если id беседы находится в бд
        print("беседа уже сохранена")
        return

    # получение информации о беседе
    chat_info: dict = api_methods.messages.get_conversations_by_id(peer_id=peer_id)
    try:
        # попытка инициализации полей модели Chat
        chat_vk_id: int = peer_id
        chat_name: str = chat_info["items"][0]["chat_settings"]["title"]

        # сохранение новой записи
        Chat(chat_vk_id=chat_vk_id, chat_name=chat_name).save()
        print(f"{chat_name} сохранен")
    except IndexError:
        """
        если выбрасывается IndexError, то бот не может получить доступ к данным
        о беседе, потому что не является администратором беседы.

        в этом случае выходим из функции с сообщением об ошибке.
        """
        return api_methods.messages.send(
            peer_id=peer_id,
            message="Ошибка! Сделайте бота администратором беседы."
        )

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
                        start_command(
                            peer_id=longpoll_updates[0]["object"]["message"]["peer_id"]
                        )
                        print("продолжение работы")

        # изменение ts для следующего запроса
        # ts - номер последнего события, начиная с которого нужно получать данные;
        ts = longpoll_response["ts"]
