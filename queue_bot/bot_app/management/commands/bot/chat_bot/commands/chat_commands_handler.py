from bot_app.management.commands.bot.bot_commands.command import BotCommand
from bot_app.management.commands.bot.bot_commands.commands_exceptions import CommandNotExistError
from bot_app.management.commands.bot.chat_bot.commands.commands import ChatInvitationCommand, ChatStartCommand
from bot_app.management.commands.bot.utils.server.responses import Event
from bot_app.management.commands.bot.bot_commands.commands_handler import CommandsHandler


BOT_NAME: str = "[club206732640|@bboot]"


class ChatCommandsHandler(CommandsHandler):
    """ обработчик команд из бесед """

    def __init__(self) -> None:
        super().__init__()
        self._commands[""] = ChatInvitationCommand()
        self._commands["start"] = ChatStartCommand()

    def handle(self, event: Event) -> None:
        try:
            command: BotCommand = self._commands[event.text.lstrip(BOT_NAME).lstrip(" ").lower()]
            command.start(event=event)
        except KeyError:
            raise CommandNotExistError()

