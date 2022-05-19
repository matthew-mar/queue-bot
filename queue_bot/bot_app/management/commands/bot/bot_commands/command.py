from typing import Any
from bot_app.management.commands.bot.vk_api.vk_api import Session, VkApiMethods
from abc import ABC
from bot_app.management.commands.bot.vk_api.longpoll.responses import Event


class BotCommand(ABC):
    """
    абстрактный клаcc, описывающий работу команды бота
    """

    def __init__(self) -> None:
        """
        команда инициализируется объектом VkApiNethods
        для получения доступа к методам vk api
        """
        self.api: VkApiMethods = Session().api
        self.command_ended: bool = False
    
    def start(self, event: Event, **kwargs) -> Any:
        """
        виртуальная функция для начала выполнения команды

        входные параметры:
        event: событие с VkLongPoll сервера
        """
        self.command_ended = False
