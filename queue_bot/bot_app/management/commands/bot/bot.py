from abc import ABC
from bot_app.management.commands.bot.bot_commands.commands_handler import CommandsHandler
from bot_app.management.commands.bot.vk_api.vk_api import Session, VkApiMethods
from bot_app.management.commands.bot.vk_api.longpoll.longpoll import Longpoll


class Bot(ABC):
    """ абстрактный класс бота """

    GROUP_ID: int = 206732640

    vk_session: Session = Session()  # установление сессии с вк
    vk_api: VkApiMethods = vk_session.api  # получение доступа к api
    longpoll: Longpoll = Longpoll(group_id=GROUP_ID)  # подключение к LongPoll серверу

    def __init__(self, commands_handler: CommandsHandler) -> None:
        """ 
        бот инициализируется обработчиком команд 
        от обработчика команд будет зависеть какие события будет обрабатывать бот:
        событие из бесед или диалогов
        """
        self.commands_handler: CommandsHandler = commands_handler
    
    def run(self) -> None: return None  # команда запуска бота
