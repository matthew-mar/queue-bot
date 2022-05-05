from pprint import pprint
import requests
from bot_app.management.commands.bot.utils.api import Session
from bot_app.management.commands.bot.utils.keyboard.keyboard import make_keyboard
from bot_app.management.commands.bot.utils.server.longpoll import Longpoll
from bot_app.management.commands.bot.utils.server.event import Event



GROUP_ID: int = 206732640
BOT_NAME: str = "[club206732640|@bboot]"

vk_session: Session = Session()  # установление сессии с вк
longpoll: Longpoll = Longpoll(group_id=GROUP_ID)  # подключение к LongPoll серверу


def run():
    for event in longpoll.listen():
        event: Event = event
        print(event.type)
 