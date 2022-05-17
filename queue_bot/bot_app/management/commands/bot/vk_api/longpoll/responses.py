from abc import ABC


BOT_VK_ID: int = 206732640


class EventType:
    """ типы событий LongPoll сервера """

    EMPTY_EVENT = "empty_event"

    MESSAGE_TYPING_STATE = "message_typing_state"

    MESSAGE_NEW = "message_new"

    MESSAGE_REPLY = "message_reply"

    CHAT_CICK_USER = "chat_kick_user"

    CHAT_INVITE_USER = "chat_invite_user"


class Event(ABC):
    """ событие LongPoll сервера """
    __slots__ = (  
        # поля, встречающиеся во всех событиях от сервера
        "_type",
        "_event_id",
        "_object",

        # поля, которые встречаются у сообщений
        "_group_id"
    )

    def __init__(self, obj: dict) -> None:
        if obj is None:
            obj = {}
        self._type: str = obj.get("type")
        self._event_id: str = obj.get("event_id")
        self._object: dict = obj.get("object")
        self._group_id: int = obj.get("group_id")


    @property
    def type(self) -> str:
        return self._type

    @property
    def event_id(self) -> str:
        return self._event_id
    
    @property
    def object(self) -> dict:
        return self._object

    @property
    def action(self) -> dict: return None

    @property
    def action_type(self) -> str: return None

    @property
    def keyboard(self) -> bool: return None

    @property
    def action_from_bot(self) -> bool: return None

    @property
    def attachments(self) -> list: return None

    @property
    def conversation_message_id(self) -> int: return None

    @property
    def date(self) -> int: return None

    @property
    def from_id(self) -> int: return None

    @property
    def fwd_messages(self) -> list: return None

    @property
    def id(self) -> int: return None

    @property
    def important(self) -> bool: return None
    
    @property
    def is_hidden(self) -> bool: return None

    @property
    def out(self) -> int: return None

    @property
    def peer_id(self) -> int: return None

    @property
    def random_id(self) -> int: return None

    @property
    def text(self) -> str: return None

    @property
    def from_me(self) -> bool: return None
    
    @property
    def to_me(self) -> bool: return None

    @property
    def from_chat(self) -> bool: return None

    @property
    def from_dialog(self) -> bool: return None

    @property
    def invitation_to_chat(self) -> bool: return None

    @property
    def group_id(self) -> int: return None

    @property
    def client_info(self) -> dict: return None

    @property
    def inline_keyboard(self) -> bool: return None

    @property
    def keyboard(self) -> bool: return None


class MessageNew(Event):
    """ событие нового сообщения """
    def __init__(self, obj: dict) -> None:
        super().__init__(obj)

    @property
    def action(self) -> dict:
        return self.object["message"].get("action")

    @property
    def action_type(self) -> str:
        if self.action != None:
            return self.action["type"]
        
    @property 
    def action_from_bot(self) -> bool:
        if self.action != None:
            return abs(self.action["member_id"]) == BOT_VK_ID

    @property
    def keyboard(self) -> bool:
        return self.text
    
    @property
    def attachments(self) -> list:
        return self._object["message"]["attachments"]
    
    @property
    def conversation_message_id(self) -> int:
        return self._object["message"]["conversation_message_id"]

    @property
    def date(self) -> int:
        return self._object["message"]["date"]

    @property
    def from_id(self) -> int:
        return self._object["message"]["from_id"]

    @property
    def fwd_messages(self) -> list:
        return self._object["message"]["fwd_messages"]

    @property
    def id(self) -> int:
        return self._object["message"]["id"]

    @property
    def important(self) -> bool:
        return self._object["message"]["important"]
    
    @property
    def is_hidden(self) -> bool:
        return self._object["message"]["is_hidden"]

    @property
    def out(self) -> int:
        return self._object["message"]["out"]

    @property
    def peer_id(self) -> int:
        return self._object["message"]["peer_id"]

    @property
    def random_id(self) -> int:
        return self._object["message"]["random_id"]

    @property
    def text(self) -> str:
        return self._object["message"]["text"]

    @property
    def from_me(self) -> bool:
        return self.out == 1
    
    @property
    def to_me(self) -> bool:
        return self.out == 0
    
    @property
    def from_chat(self) -> bool:
        return self.peer_id > 2_000_000_000
    
    @property
    def from_dialog(self) -> bool:
        return self.peer_id < 2_000_000_000

    @property
    def invitation_to_chat(self) -> bool:
        if self.from_chat:
            return len(self.text) == 0
    
    @property
    def group_id(self) -> int:
        return self._group_id

    @property
    def client_info(self) -> dict:
        return self.object.get("client_info")

    @property
    def inline_keyboard(self) -> bool:
        return self.client_info.get("inline_keyboard")
    
    @property
    def keyboard(self) -> bool:
        return self.client_info.get("keyboard")


class EmptyEvent(Event):
    def __init__(self, obj: dict) -> None:
        super().__init__(obj)
        self._type = "empty_event"


class MessageTypingState(Event):
    """ событие набора текста """
    def __init__(self, obj: dict) -> None:
        super().__init__(obj)


class MessageReply(MessageNew):
    def __init__(self, obj: dict) -> None:
        super().__init__(obj)

    @property
    def attachments(self) -> list:
        return self._object["attachments"]
    
    @property
    def conversation_message_id(self) -> int:
        return self._object["conversation_message_id"]

    @property
    def date(self) -> int:
        return self._object["date"]

    @property
    def from_id(self) -> int:
        return self._object["from_id"]

    @property
    def fwd_messages(self) -> list:
        return self._object["fwd_messages"]

    @property
    def id(self) -> int:
        return self._object["id"]

    @property
    def important(self) -> bool:
        return self._object["important"]
    
    @property
    def is_hidden(self) -> bool:
        return self._object["is_hidden"]

    @property
    def out(self) -> int:
        return self._object["out"]

    @property
    def peer_id(self) -> int:
        return self._object["peer_id"]

    @property
    def random_id(self) -> int:
        return self._object["random_id"]

    @property
    def text(self) -> str:
        return self._object["text"]


class LongpollResponse:
    """ обработчик ответов с сервера """

    __EVENTS: dict[str:Event] = {
        EventType.EMPTY_EVENT: EmptyEvent,
        EventType.MESSAGE_NEW: MessageNew,
        EventType.MESSAGE_TYPING_STATE: MessageTypingState,
        EventType.MESSAGE_REPLY: MessageReply,
    }

    def __init__(self, longpoll_response: dict) -> None:
        self.__response: dict = longpoll_response
    

    def get_event(self) -> Event:
        """ определение типа события """
        try:
            event_type: str = self.__response["updates"][0]["type"]
            event: Event = self.__EVENTS[event_type](obj=self.__response["updates"][0])
            return event
        except IndexError:
            """ 
            В случае когда выбрасывается IndexError на сервере нет новых
            событий и список updates пуст. Возвращаем EmptyEvent
            """
            return self.__EVENTS["empty_event"](obj=None)



class ConversationsResponse:
    """ ответ от метода api get_conversations_by_id """
    def __init__(self, conversations: dict) -> None:
        self.__conversations: dict = conversations
    
    @property
    def count(self) -> int:
        return self.__conversations["count"]
    
    @property
    def items(self) -> dict:
        items_list: list = self.__conversations["items"]
        return items_list[0] if len(items_list) > 0 else {}
    
    @property
    def peer(self) -> dict:
        return self.items.get("peer")
    
    @property
    def peer_id(self) -> int:
        return self.peer.get("id")

    @property
    def chat_settings(self) -> dict:
        return self.items.get("chat_settings")
    
    @property
    def title(self) -> str:
        return self.chat_settings.get("title")
    
    @property
    def owner_id(self) -> id:
        return self.chat_settings.get("owner_id")


class Profile:
    """ сборник данных о профиле из MembersResponse """
    def __init__(self, profile: dict):
        self.profile: dict = profile
    
    @property
    def first_name(self) -> str:
        return self.profile["first_name"]
    
    @property
    def user_id(self) -> int:
        return self.profile["id"]
    
    @property
    def last_name(self) -> str:
        return self.profile["last_name"]


class MembersResponse:
    """ обработчик ответа от метода api messages.get_conversation_members """
    def __init__(self, members: dict) -> None:
        self.__members_response: dict = members
    
    @property
    def profiles(self) -> list[Profile]:
        profiles: list[dict] = self.__members_response.get("profiles")
        if profiles != None:
            return list(map(Profile, profiles))


class UsersResponse:
    """ обработчик ответа от метода api users.get """
    def __init__(self, user_response: dict) -> None:
        self.__user: dict = user_response

    @property
    def user(self) -> dict:
        return self.__user
    
    @property
    def id(self) -> int:
        return self.user["id"]
    
    @property
    def first_name(self) -> str:
        return self.user["first_name"]
    
    @property
    def last_name(self) -> str:
        return self.user["last_name"]
