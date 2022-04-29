from bot_app.management.commands.bot.dialog_bot.commands.command import BotCommand
from bot_app.management.commands.bot.dialog_bot.commands.start.start import StartCommand
from bot_app.management.commands.bot.dialog_bot.commands.queue.queue_creator import QueueCreateCommand

from vk_api.longpoll import Event


class CommandNotExistError(Exception):
    pass


class CommandsHandler:
    """
    обработчик команд
    """

    def __init__(self) -> None:
        """
        инициализируется объектом VkApiMethods для получения доступа к vk api
        """
        # команды, которые может обрабатывать бот
        self.__commands: dict[str:BotCommand] = {
            "начать": StartCommand(),
            "создать очередь": QueueCreateCommand()
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
        if isinstance(command_result, str):
            if command_result == "stop":
                self.__current_command.pop(event.user_id)
            else:
                self.__current_command[event.user_id] = command_result


if __name__ == "__main__":
    pass
