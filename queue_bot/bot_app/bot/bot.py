import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id


def read_token() -> str:
    """ функция считывает токен из файла """
    with open("./token.txt", "r") as token:
        token: str = token.read()
    return token


def message_send(user_id: int, message: str) -> None:
    """ 
    функция реализует метод vk api messages.send 
    описание метода: https://dev.vk.com/method/messages.send
    """
    api.messages.send(**{
        "user_id": event.user_id,
        "random_id": get_random_id(),
        "message": event.text,
    })


if __name__ == "__main__":
    # авторизация
    session = vk_api.VkApi(token=read_token())  # создание новой сессии бота
    api = session.get_api()  # получение доступа к методам vk api
    longpoll = VkLongPoll(session)  # подключение к longpoll серверу

    # "прослушивание" сервера
    for event in longpoll.listen():
        # эхо-бот
        if event.to_me and event.type == VkEventType.MESSAGE_NEW:
            message_send(user_id=event.user_id, message=event.text)
