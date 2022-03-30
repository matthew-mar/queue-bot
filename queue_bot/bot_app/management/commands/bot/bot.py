from pprint import pprint
from requests import post
import vk
from vk_api.utils import get_random_id
from django.conf import settings
import django
django.setup()
from ....models import Member


GROUP_ID: int = 206732640
VK_API_VERSION: float = 5.131
BOT_DIR: str = "/".join(__file__.split("/")[:-1])


def read_token() -> str:
    """ функция считывает токен из файла """
    with open(f"{BOT_DIR}/token.txt") as token_file:
        token: str = token_file.read()
    return token


def messages_send(peer_id: int, message: str) -> None:
    """ 
    отправка сообщения через метод vk api messages.send 
    описание метода: https://vk.com/dev/messages.send
    """
    api.messages.send(**{
        "peer_id": peer_id,
        "random_id": get_random_id,
        "message": message,
    })


def users_get(user_ids: int) -> dict:
    """
    получение данных о пользователе через метод vk api users.get
    описание метода: https://dev.vk.com/method/users.get
    """
    users: list[dict] = api.users.get(**{
        "user_ids": user_ids
    })
    return users[0]


def start() -> None:
    # получение доступа к серверу
    longpoll: dict = api.groups.getLongPollServer(group_id=GROUP_ID)
    server, key, ts = longpoll["server"], longpoll["key"], longpoll["ts"]

    # прослушивание сервера
    while True:
        longpoll_response: dict = post(server, data={  # получение ответа
            "act": "a_check",
            "key": key,
            "ts": ts,
            "wait": 25
        }).json()

        # получение списка событий от сервера
        longpoll_updates: list = longpoll_response["updates"]
        if longpoll_updates:  # если обновления есть
            print(longpoll_updates)
            # если получено новое сообщение
            if len(longpoll_updates[0]["object"]["message"]["text"]) == 0:
                admins_vk_ids = [
                    admin.member_vk_id 
                    for admin in Member.objects.filter(is_admin=True)
                ]
                if longpoll_updates[0]["object"]["message"]["from_id"] not in admins_vk_ids:
                    admin: dict = users_get(longpoll_updates[0]["object"]["message"]["from_id"])
                    member: Member = Member(
                        member_vk_id=admin["id"],
                        is_admin=True,
                        name=admin["first_name"],
                        surname=admin["last_name"],
                    )
                    member.save()
                    print("new admin")

        # изменение ts для следующего запроса
        # ts - номер последнего события, начиная с которого нужно получать данные;
        ts = longpoll_response["ts"]


# авторизация
session: vk.Session = vk.Session(access_token=read_token())
api: vk.API = vk.API(session, v=VK_API_VERSION)
