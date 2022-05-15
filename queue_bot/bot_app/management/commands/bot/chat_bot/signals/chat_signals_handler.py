from bot_app.management.commands.bot.bot_signals.signal import Signal
from bot_app.management.commands.bot.bot_signals.signals_handler import SignalsHandler
from bot_app.management.commands.bot.chat_bot.signals.signals import NewQueueSignal


class ChatSignalsHandler(SignalsHandler):
    def __init__(self) -> None:
        super().__init__()
        self._signals["new_queue"] = NewQueueSignal
    
    def handle(self, signal_name: str, args: dict) -> None:
        signal: Signal = self._signals[signal_name](
            signal_name=signal_name,
            args=args
        )
        signal.execute()
