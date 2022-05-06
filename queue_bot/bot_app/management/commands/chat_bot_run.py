from django.core.management.base import BaseCommand
from django.utils import timezone
from bot_app.management.commands.bot.chat_bot.chat_bot import chat_bot


class Command(BaseCommand):
    help = 'Displays current time'

    def handle(self, *args, **kwargs):
        print("bot started")        
        chat_bot.run()
