from bot_app.management.commands.bot.bot_signals.signals_handler import SignalsHandler


class DialogSignalsHandler(SignalsHandler):
    def __init__(self) -> None:
        super().__init__()
    
    def handle(self, signal_name: str, data: dict) -> None:
        return super().handle(signal_name, data)