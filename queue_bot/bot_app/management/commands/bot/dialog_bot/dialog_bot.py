from bot_app.management.commands.bot.utils.api import Session, VkApiMethods
from vk_api.longpoll import VkLongPoll, VkEventType
from bot_app.management.commands.bot.dialog_bot.commands.commands_handler import (
    CommandNotExistError, CommandsHandler)
from pprint import pprint


GROUP_ID: int = 206732640


session: Session = Session(group_id=GROUP_ID)
api: VkApiMethods = session.api
commands_handler: CommandsHandler = CommandsHandler()


def run():
    longpoll: VkLongPoll = VkLongPoll(session.session) 

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                try:
                    # отправляем событие на обработку обработчику команд
                    commands_handler.handle(event=event)
                except CommandNotExistError as error:
                    session.api.messages.send(
                        peer_id=event.peer_id,
                        message=error.args[0]
                    )
                
