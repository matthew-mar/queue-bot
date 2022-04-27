import django
django.setup()

from ...utils.bot_utils import VkApiMethods
from abc import ABC


class BotCommand(ABC):
    """
    абстрактный клаcc, описывающий работу команды бота
    """

    def __init__(self, api: VkApiMethods) -> None:
        """
        команда инициализируется объектом VkApiNethods
        для получения доступа к методам vk api
        """
        self.api = api
    
    def start(self, event, **kwargs) -> None:
        """
        виртуальная функция для начала выполнения команды

        входные параметры:
        event: событие с VkLongPoll сервера
        """
        pass
