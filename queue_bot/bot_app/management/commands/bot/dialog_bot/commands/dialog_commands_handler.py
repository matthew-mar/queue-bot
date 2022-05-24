from bot_app.management.commands.bot.bot_commands.command import BotCommand
from bot_app.management.commands.bot.bot_commands.commands_exceptions import CommandNotExistError
from bot_app.management.commands.bot.bot_commands.commands_handler import CommandsHandler
from bot_app.management.commands.bot.dialog_bot.commands.commands import DialogStartCommand, GetQueuePlaceCommand, QueueCreateCommand, QueueEnrollCommand, QueueQuitCommand
from bot_app.management.commands.bot.vk_api.longpoll.responses import Event


class DialogCommandsHandler(CommandsHandler):
    """ обработчик команд в личных сообщениях """
    def __init__(self) -> None:
        super().__init__()
        self._commands["начать"] = DialogStartCommand()
        self._commands["создать очередь"] = QueueCreateCommand()
        self._commands["записаться в очередь"] = QueueEnrollCommand()
        self._commands["удалиться из очереди"] = QueueQuitCommand()
        self._commands["получить место в очереди"] = GetQueuePlaceCommand()

    def handle(self, event: Event) -> None:
        try:
            command_text: str = event.text.lower()
            
            if event.from_id in self._current_command:
                if self._commands[self._current_command[event.from_id]].command_ended:
                    self._current_command[event.from_id] = command_text
            else:
                self._current_command[event.from_id] = command_text
                
            command: BotCommand = self._commands[self._current_command[event.from_id]]
            command.start(event)
        except KeyError:
            self._current_command.pop(event.from_id)
            raise CommandNotExistError()
