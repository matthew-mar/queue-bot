import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id


def read_token() -> str:
    with open("./token.txt", "r") as token:
        token: str = token.read()
    return token


# авторизация
session = vk_api.VkApi(token=read_token())
api = session.get_api()
longpoll = VkLongPoll(session)
