from pprint import pprint
import requests
from bot_app.management.commands.bot.utils.api import Session, VkApiMethods
from bot_app.management.commands.bot.utils.server.responses import LongpollResponse, Event


class Longpoll:
    """ работа с Longpoll сервером """
    __instance = None

    def __new__(cls, group_id: int) -> "Longpoll":
        if cls.__instance is None:
            cls.__instance = super(Longpoll, cls).__new__(cls)
            cls.__session: Session = Session()
            cls.__api: VkApiMethods = cls.__session.api
            cls.__longpoll: dict = cls.__api.groups.get_longpoll_server(group_id=group_id)
        return cls.__instance
    
    def listen(cls) -> Event:
        server, key, ts = cls.__longpoll["server"], cls.__longpoll["key"], cls.__longpoll["ts"]
        while True:
            longpoll_response: dict = requests.post(url=server, data={
                "act": "a_check",
                "key": key,
                "ts": ts,
                "wait": 25
            }).json()
            # pprint(longpoll_response)
            response: LongpollResponse = LongpollResponse(longpoll_response=longpoll_response)
            yield response.get_event()
            ts = longpoll_response["ts"]
