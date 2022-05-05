import vk
from bot_app.management.commands.bot.utils.bot_utils import read_token
from abc import ABC
from vk_api.utils import get_random_id


class VkApiMethods:
    """ методы vk api """
    def __init__(self, api: vk.API) -> None:
        self.users = Users(api)
        self.groups = Groups(api)
        self.messages = Messages(api)


class ApiSection(ABC):
    """ группа методов vk api """
    def __init__(self, api: vk.API) -> None:
        self.api: vk.API = api


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

    def get_conversation_members(self, peer_id: int) -> dict:
        """
        получение данных об участниках беседы через метод vk api messages.getConversationMembers
        описание метода: https://dev.vk.com/method/messages.getConversationMembers
        """
        members_info: dict = self.api.messages.getConversationMembers(**{
            "peer_id": peer_id
        })
        return members_info


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


class Session:
    """ класс описывает взаимодействие с vk api """
    __instance = None
    
    __VK_API_VERSION: float = 5.131

    def __new__(cls) -> "Session":
        if cls.__instance is None:
            cls.__instance = super(Session, cls).__new__(cls)
            cls.__session = vk.Session(access_token=read_token())
            cls.__api = VkApiMethods(vk.API(session=cls.__session, v=cls.__VK_API_VERSION))
        return cls.__instance

    @property
    def api(cls) -> VkApiMethods:
        """ свойство доступа к методам api """
        return cls.__api
