from bot_app.management.commands.bot.bot import Bot
from bot_app.management.commands.bot.bot_commands.commands_exceptions import CommandNotExistError
from bot_app.management.commands.bot.dialog_bot.commands.dialog_commands_handler import DialogCommandsHandler
from bot_app.management.commands.bot.vk_api.longpoll.responses import Event


class DialogBot(Bot):
    """ бот обработчик личных сообщений """
    def run(self) -> None:
        for event in self.longpoll.listen():
            event: Event = event
            if event.from_dialog:
                if event.to_me:
                    try:
                        self.commands_handler.handle(event=event)
                    except CommandNotExistError:
                        self.vk_api.messages.send(
                            peer_id=event.peer_id,
                            message="несуществующая команда"
                        )


dialog_bot: DialogBot = DialogBot(commands_handler=DialogCommandsHandler())
