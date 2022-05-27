from abc import ABC
from bot_app.management.commands.bot.bot_signals.signal import Signal


class SignalsHandler(ABC):
    """ обработчик сигналов с сервера """
    def __init__(self) -> None:
        super().__init__()
        self._signals: dict[str:Signal] = {}
    
    def handle(self, signal_name: str, args: dict) -> None: 
        signal: Signal = self._signals[signal_name](
            signal_name=signal_name,
            args=args
        )
        signal.execute()
