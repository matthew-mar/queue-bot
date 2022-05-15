from abc import ABC
from bot_app.management.commands.bot.bot_signals.signal import Signal


class SignalsHandler(ABC):
    """ обработчик сигналов с сервера """
    def __init__(self) -> None:
        super().__init__()
        self._signals: dict[str:Signal] = {}
    
    def handle(self, signal_name: str, args: dict) -> None: return None
