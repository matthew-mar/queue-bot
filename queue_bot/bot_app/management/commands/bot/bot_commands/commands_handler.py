from bot_app.management.commands.bot.vk_api.longpoll.responses import Event
from bot_app.management.commands.bot.bot_commands.command import BotCommand
from abc import ABC


class CommandsHandler(ABC):
    """ Абстрактный класс обработчика команд """

    def __init__(self) -> None:
        # команды, которые может обрабатывать бот
        self._commands: dict[str:BotCommand] = {}

        # словарь для хранения текущей команды
        # ключом является event.user_id значением является текст команды, 
        # на которой находится пользователь
        self._current_command: dict[int:str] = {}

    def handle(self, event: Event) -> None: 
        """ 
        Обработка команд 
        
        :event (Event)
            событие с longpoll сервера.
        """
        return None
