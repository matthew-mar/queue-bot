from bot_app.management.commands.bot.bot_commands.command import BotCommand
from bot_app.management.commands.bot.bot_commands.commands_exceptions import CommandNotExistError
from bot_app.management.commands.bot.bot_commands.commands_handler import CommandsHandler
from bot_app.management.commands.bot.dialog_bot.commands.commands import DialogStartCommand
from bot_app.management.commands.bot.utils.server.responses import Event


class DialogCommandsHandler(CommandsHandler):
    """ обработчик команд в личных сообщениях """
    def __init__(self) -> None:
        super().__init__()
        self._commands["start"] = DialogStartCommand()

    def handle(self, event: Event) -> None:
        try:
            command: BotCommand = self._commands[event.text.lower()]
            command.start(event)
        except KeyError:
            raise CommandNotExistError()
