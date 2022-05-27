""" Вспомогательные функции для взаимодействием с api бота """


import json
from bot_app.bot_api.bot_api import BotApi


bot_api: BotApi = BotApi()


def send_signal(to: str, data: dict) -> None:
    """
    Отправка сигнала через метод api бота send_signal
    """
    bot_api.send_signal(to=to, data={"data": json.dumps(data)})
