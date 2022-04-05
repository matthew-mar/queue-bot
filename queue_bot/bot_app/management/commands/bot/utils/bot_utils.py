import django
django.setup()

import vk
from vk_api.utils import get_random_id
import json
from pprint import pprint
from .....models import Chat, ChatMember, Member
from week import Week
import datetime


BOT_DIR: str = "/".join(__file__.split("/")[:-1])

week_days: dict[str:int] = {  # словарь соответствий дня недели с его номером
    "понедельник": 1,
    "вторник": 2,
    "среда": 3,
    "четверг": 4,
    "пятница": 5,
    "суббота": 6,
    "воскресенье": 7
}


def read_token() -> str:
    """ функция считывает токен из файла """
    with open(f"{BOT_DIR}/token.txt") as token_file:
        token: str = token_file.read()
    return token


def get_days() -> list[str]:
    """ функция отправляет список доступных дней для пользователя """
    days: list[str] = []
    today: int = datetime.date.today().weekday() + 1
    for day in week_days:
        if week_days[day] >= today:
            days.append(day)
    return days


def get_datetime(day: int, hours: int, minutes: int) -> datetime:
    """ возвращает дату и время начала очереди """
    return datetime.datetime(
        year=int(Week.thisweek().startdate.strftime("%Y")),
        month=int(Week.thisweek().startdate.strftime("%m")),
        day=int(Week.thisweek().startdate.strftime("%d")) + day-1,
        hour=hours,
        minute=minutes
    )


class VkApiMethods:
    """ методы vk api """
    def __init__(self, api: vk.API) -> None:
        self.api = api
        self.users = Users(self.api)
        self.groups = Groups(self.api)
        self.messages = Messages(self.api)


class ApiSection:
    """ группа методов vk api """
    def __init__(self, api: vk.API) -> None:
        self.api = api


class Messages(ApiSection):
    """ группа методов messages """
    def __init__(self, api: vk.API) -> None:
        super().__init__(api)
    
    def send(self, peer_id: int, message: str, keyboard: str = "") -> None:
        """ 
        отправка сообщения через метод vk api messages.send 
        описание метода: https://vk.com/dev/messages.send
        """
        self.api.messages.send(**{
            "peer_id": peer_id,
            "random_id": get_random_id(),
            "message": message,
            "keyboard": keyboard
        })
    
    def get_conversations_by_id(self, peer_id: int) -> dict:
        """
        получение данных о беседе через метод vk api messages.getConversationsById
        описание метода: https://vk.com/dev/messages.getConversationsById
        """
        conversations: list[dict] = self.api.messages.getConversationsById(**{
            "peer_ids": peer_id
        })
        return conversations

    def get_conversation_members(self, peer_id: int) -> list:
        """
        получение данных об участниках беседы через метод vk api messages.getConversationMembers
        описание метода: https://dev.vk.com/method/messages.getConversationMembers
        """
        members_info: dict = self.api.messages.getConversationMembers(**{
            "peer_id": peer_id
        })
        return members_info["profiles"]


class Users(ApiSection):
    """ группа методов users """
    def __init__(self, api: vk.API) -> None:
        super().__init__(api)
    
    def get(self, user_ids: int) -> dict:
        """
        получение данных о пользователе через метод vk api users.get
        описание метода: https://dev.vk.com/method/users.get
        """
        users: list[dict] = self.api.users.get(**{
            "user_ids": user_ids
        })
        return users[0]


class Groups(ApiSection):
    """ группа методов groups """
    def __init__(self, api: vk.API) -> None:
        super().__init__(api)
    
    def get_longpoll_server(self, group_id: int) -> dict:
        """
        получение данных о longpoll сервере через метод vk api groups.getLongPollServer
        описание метода: https://dev.vk.com/method/groups.getLongPollServer
        """
        return self.api.groups.getLongPollServer(**{
            "group_id": group_id
        })


if __name__ == "__main__":
    with open(f"{BOT_DIR}/keyboard.json", "r") as keyboard_file:
        keyboard: str = keyboard_file.read()
        keyboard = json.loads(keyboard)
    
    keyboard = json.dumps(keyboard, indent=2)
    print(keyboard, type(keyboard))


if __name__ == "__main__":
    pass