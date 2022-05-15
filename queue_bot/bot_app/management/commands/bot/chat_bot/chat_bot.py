from pprint import pprint
from bot_app.management.commands.bot.bot import Bot
from bot_app.management.commands.bot.bot_commands.commands_exceptions import CommandNotExistError
from bot_app.management.commands.bot.chat_bot.commands.chat_commands_handler import ChatCommandsHandler
from bot_app.management.commands.bot.vk_api.longpoll.responses import Event, EventType


class ChatBot(Bot):
    """ бот обработчик бесед """
    def run(self) -> None:
        for event in self.longpoll.listen():
            event: Event = event
            if event.from_chat:
                if event.type == EventType.MESSAGE_NEW:
                    try:
                        self.commands_handler.handle(event=event)
                    except CommandNotExistError:
                        self.vk_api.messages.send(
                            peer_id=event.peer_id,
                            message="несуществующая команда"
                        )


chat_bot: ChatBot = ChatBot(commands_handler=ChatCommandsHandler())
