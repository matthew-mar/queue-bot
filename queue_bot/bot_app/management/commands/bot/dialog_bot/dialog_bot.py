import django
django.setup()

from ..utils.bot_utils import read_token, VkApiMethods, week_days, get_days, get_datetime
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType
from ..utils.keyboard.keyboard import make_keyboard
from .....models import ChatMember, Member, Chat, Queue, QueueChat
from datetime import datetime
from pprint import pprint
from .utils import is_owner
from .commands.commands_handler import CommandNotExistError, CommandsHandler


# авторизация
session: VkApi = VkApi(token=read_token())
api_methods: VkApiMethods = VkApiMethods(api=session.get_api())
commands_handler: CommandsHandler = CommandsHandler(api=api_methods)


def run():
    longpoll: VkLongPoll = VkLongPoll(session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                try:
                    # отправляем событие на обработку обработчику команд
                    commands_handler.handle(event=event)
                except CommandNotExistError as error:
                    api_methods.messages.send(
                        peer_id=event.peer_id,
                        message=error.args[0]
                    )
