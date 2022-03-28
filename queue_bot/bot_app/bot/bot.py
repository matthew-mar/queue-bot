from requests import post
import vk
from vk_api.utils import get_random_id

GROUP_ID: int = 206732640
VK_API_VERSION: float = 5.131


def read_token() -> str:
    """ функция считывает токен из файла """
    with open("token.txt", "r") as token_file:
        token: str = token_file.read()
    return token


def messages_send(peer_id: int, message: str) -> None:
    """ 
    отправка сообщения через метод vk api messages.send 
    описание метода: https://vk.com/dev/messages.send
    """
    api.messages.send(**{
        "peer_id": peer_id,
        "random_id": get_random_id(),
        "message": message,
    })


if __name__ == "__main__":
    # авторизация
    session: vk.Session = vk.Session(access_token=read_token())
    api: vk.API = vk.API(session, v=VK_API_VERSION)
    
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
            # если получено новое сообщение
            if longpoll_updates[0]["type"] == "message_new":
                messages_send(  # отправка сообщения с текстом сообшения участника беседы
                    peer_id=longpoll_updates[0]["object"]["message"]["peer_id"],
                    message=longpoll_updates[0]["object"]["message"]["text"].lstrip("[club206732640|bot] "),
                )

        # изменение ts для следующего запроса
        # ts - номер последнего события, начиная с которого нужно получать данные;
        ts = longpoll_response["ts"]
