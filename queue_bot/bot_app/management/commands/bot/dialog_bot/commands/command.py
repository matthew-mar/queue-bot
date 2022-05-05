from typing import Any
from bot_app.management.commands.bot.utils.api import Session
from abc import ABC


class BotCommand(ABC):
    """
    абстрактный клаcc, описывающий работу команды бота
    """

    def __init__(self) -> None:
        """
        команда инициализируется объектом VkApiNethods
        для получения доступа к методам vk api
        """
        self.api: Session = Session()
    
    def start(self, event, **kwargs) -> Any:
        """
        виртуальная функция для начала выполнения команды

        входные параметры:
        event: событие с VkLongPoll сервера
        """
        pass
