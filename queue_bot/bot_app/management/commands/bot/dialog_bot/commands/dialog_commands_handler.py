from bot_app.management.commands.bot.bot_commands.command import BotCommand
from bot_app.management.commands.bot.bot_commands.commands_exceptions import CommandNotExistError
from bot_app.management.commands.bot.bot_commands.commands_handler import CommandsHandler
from bot_app.management.commands.bot.dialog_bot.commands.commands import DialogStartCommand, QueueCreateCommand
from bot_app.management.commands.bot.vk_api.longpoll.responses import Event


class DialogCommandsHandler(CommandsHandler):
    """ обработчик команд в личных сообщениях """
    def __init__(self) -> None:
        super().__init__()
        self._commands["start"] = DialogStartCommand()
        self._commands["создать очередь"] = QueueCreateCommand()

    def handle(self, event: Event) -> None:
        try:
            command_text: str = event.text.lower()
            if event.from_id in self._current_command:
                if self._commands["создать очередь"].queue_saved(event.from_id):
                    self._current_command.pop(event.from_id)
            if command_text == "создать очередь":
                self._current_command[event.from_id] = "создать очередь"
            if self._current_command.get(event.from_id) != None:
                command_text: str = self._current_command[event.from_id]
            command: BotCommand = self._commands[command_text]
            command.start(event)
        except KeyError:
            raise CommandNotExistError()
