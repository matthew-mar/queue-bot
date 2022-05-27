from bot_app.management.commands.bot.bot_signals.signals_handler import SignalsHandler
from bot_app.management.commands.bot.dialog_bot.signals.signals import NextInQueueSignal, QueueEnrollFromChatSignal


class DialogSignalsHandler(SignalsHandler):
    def __init__(self) -> None:
        super().__init__()
        self._signals["queue_enroll_from_chat"] = QueueEnrollFromChatSignal
        self._signals["next_in_queue_signal"] = NextInQueueSignal
    
    def handle(self, signal_name: str, args: dict) -> None:
        return super().handle(signal_name, args)
