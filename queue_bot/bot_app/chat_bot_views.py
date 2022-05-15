from pprint import pprint
from rest_framework.decorators import api_view
from rest_framework.response import Response
from bot_app.management.commands.bot.chat_bot.chat_bot import chat_bot
import json


@api_view(["GET", "POST"])
def get_signal(request, to: str):
    if request.method == "POST":
        if to == "chat":
            data: dict = json.loads(request.data["data"])
            chat_bot.signals_handler.handle(
                signal_name=data["signal_name"],
                args=data["args"]
            )
    return Response({"get": 200})
