from bot_app.management.commands.bot.utils.api import Api
from vk_api.longpoll import VkLongPoll, VkEventType
from bot_app.management.commands.bot.dialog_bot.commands.commands_handler import (
    CommandNotExistError, CommandsHandler)
from pprint import pprint


api: Api = Api()
commands_handler: CommandsHandler = CommandsHandler()


def run():
    longpoll: VkLongPoll = VkLongPoll(api.session) 

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                try:
                    # отправляем событие на обработку обработчику команд
                    commands_handler.handle(event=event)
                except CommandNotExistError as error:
                    api.methods.messages.send(
                        peer_id=event.peer_id,
                        message=error.args[0]
                    )
                
