import django
django.setup()

from .command import BotCommand
from ...utils.bot_utils import VkApiMethods
from .start.start import StartCommand
from .queue.queue_creator import QueueCreateCommand
from vk_api.longpoll import Event


class CommandNotExistError(Exception):
    pass


class CommandsHandler:
    """
    обработчик команд
    """

    def __init__(self, api: VkApiMethods) -> None:
        """
        инициализируется объектом VkApiMethods для получения доступа к vk api
        """
        # подключение к методам VkApi
        self.__api: VkApiMethods = api

        # команды, которые может обрабатывать бот
        self.__commands: dict[str:BotCommand] = {
            "начать": StartCommand(self.__api),
            "создать очередь": QueueCreateCommand(self.__api)
        }

        # словарь для хранения текущей команды
        # ключом является event.user_id значением является текст команды, 
        # на которой находится пользователь
        self.__current_command: dict[int:str] = {}

    def handle(self, event: Event) -> None:
        """ 
        обработка команд 
        
        входные параметры:
        event: событие с VkLongPoll сервера
        """
        if event.user_id not in self.__current_command:
            # если пользователя не находится в процессе выполнения какой-либо команды
            # инициализируем стартовую команду для пользователя
            self.__current_command[event.user_id] = "начать"
        elif self.__current_command[event.user_id] != "создать очередь":
            self.__current_command[event.user_id] = event.text.lower()
        
        # получение команды пользователя
        command: BotCommand = self.__commands.get(self.__current_command[event.user_id])
        
        if command == None:
            raise CommandNotExistError(f"не существует команды {event.text}")
        
        command_result = command.start(event=event)
        if command_result != "stop":
            self.__current_command[event.user_id] = command_result
        else:
            self.__current_command.pop(event.user_id)


if __name__ == "__main__":
    pass
