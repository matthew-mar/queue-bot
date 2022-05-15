from abc import ABC
from bot_app.management.commands.bot.vk_api.vk_api import VkApiMethods, Session


class Signal(ABC):
    """ модель сигнала, приходящего с сервера """
    def __init__(self, signal_name: str, args: dict) -> None:
        self.name: str = signal_name
        self.api: VkApiMethods = Session().api
    
    def execute(self) -> None: return None

