from abc import ABC


class Event(ABC):
    """ событие LongPoll сервера """
    __slots__ = (  
        # поля, встречающиеся во всех событиях от сервера
        "__type",
        "__event_id",
        "__object",
    )

    def __init__(self, obj: dict) -> None:
        if obj is None:
            self.__type: str = "empty_event"
            self.__event_id = None
            self.__object = None
        else:
            self.__type: str = obj["type"]
            self.__event_id: str = obj["event_id"]
            self.__object: dict = obj["object"]

    @property
    def type(self) -> str:
        return self.__type

    @property
    def event_id(self) -> str:
        return self.__event_id
    
    @property
    def object(self) -> dict:
        return self.__object

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


class MessageNew(Event):
    """ событие нового сообщения """
    def __init__(self, obj: dict) -> None:
        super().__init__(obj)
    
    @property
    def attachments(self) -> list:
        return self.__object["message"]["attachments"]
    
    @property
    def conversation_message_id(self) -> int:
        return self.__object["message"]["conversation_message_id"]

    @property
    def date(self) -> int:
        return self.__object["message"]["date"]

    @property
    def from_id(self) -> int:
        return self.__object["message"]["from_id"]

    @property
    def fwd_messages(self) -> list:
        return self.__object["message"]["fwd_messages"]

    @property
    def id(self) -> int:
        return self.__object["message"]["id"]

    @property
    def important(self) -> bool:
        return self.__object["message"]["important"]
    
    @property
    def is_hidden(self) -> bool:
        return self.__object["message"]["is_hidden"]

    @property
    def out(self) -> int:
        return self.__object["message"]["out"]

    @property
    def peer_id(self) -> int:
        return self.__object["message"]["peer_id"]

    @property
    def random_id(self) -> int:
        return self.__object["message"]["random_id"]

    @property
    def text(self) -> str:
        return self.__object["message"]["text"]


class EmptyEvent(Event):
    def __init__(self, obj: dict) -> None:
        super().__init__(obj)


class MessageTypingState(Event):
    """ событие набора текста """
    def __init__(self, obj: dict) -> None:
        super().__init__(obj)


class Response:
    """ обработчик ответов с сервера """

    __EVENTS: dict[str:Event] = {
        "empty_event": EmptyEvent,
        "message_new": MessageNew,
        "message_typing_state": MessageTypingState
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
        
