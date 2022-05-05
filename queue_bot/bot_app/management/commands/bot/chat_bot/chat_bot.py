from pprint import pprint
from bot_app.management.commands.bot.bot_commands.commands_exceptions import CommandNotExistError
from bot_app.management.commands.bot.chat_bot.commands.chat_commands_handler import ChatCommandsHandler
from bot_app.management.commands.bot.utils.api import Session, VkApiMethods
from bot_app.management.commands.bot.utils.keyboard.keyboard import make_keyboard
from bot_app.management.commands.bot.utils.server.longpoll import Longpoll
from bot_app.management.commands.bot.utils.server.responses import Event, EventType


GROUP_ID: int = 206732640
BOT_NAME: str = "[club206732640|@bboot]"

vk_session: Session = Session()  # установление сессии с вк
api: VkApiMethods = vk_session.api
longpoll: Longpoll = Longpoll(group_id=GROUP_ID)  # подключение к LongPoll серверу
commands_handler: ChatCommandsHandler = ChatCommandsHandler()


def run():
    for event in longpoll.listen():
        event: Event = event
        if event.from_chat:
            if event.type == EventType.MESSAGE_NEW:
                try:
                    commands_handler.handle(event=event)
                except CommandNotExistError:
                    api.messages.send(
                        peer_id=event.peer_id,
                        message="несуществующая команда"
                    )
 