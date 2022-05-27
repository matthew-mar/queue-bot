from bot_app.management.commands.bot.bot_commands.command import BotCommand
from bot_app.management.commands.bot.bot_commands.commands_exceptions import CommandNotExistError

from bot_app.management.commands.bot.chat_bot.commands.commands import (
    ChatInvitationCommand, ChatStartCommand, CickUserCommand, 
    QueueEnrollCommand, InviteUserCommand)

from bot_app.management.commands.bot.vk_api.longpoll.responses import Event, EventType
from bot_app.management.commands.bot.bot_commands.commands_handler import CommandsHandler


BOT_NAME: str = "[club206732640|@bboot]"


class ChatCommandsHandler(CommandsHandler):
    """ Обработчик команд из бесед """

    def __init__(self) -> None:
        super().__init__()
        self._commands["start"] = ChatStartCommand()
        self._commands["записаться в"] = QueueEnrollCommand()

    def handle(self, event: Event) -> None:
        try:
            command_text: str = event.text.lstrip(BOT_NAME).lstrip(" ").lower()
            
            if command_text == "":
                if event.action_type == EventType.CHAT_CICK_USER:
                    self._commands[""] = CickUserCommand()
                elif event.action_type == EventType.CHAT_INVITE_USER:
                    if event.action_from_bot:
                        self._commands[""] = ChatInvitationCommand()
                    else:
                        self._commands[""] = InviteUserCommand()

            if "записаться в" in command_text:
                command_text = "записаться в"
            
            command: BotCommand = self._commands[command_text]
            command.start(event=event)
        except KeyError:
            raise CommandNotExistError()
