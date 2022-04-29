from django.core.management.base import BaseCommand
from django.utils import timezone
from bot_app.management.commands.bot.dialog_bot import dialog_bot


class Command(BaseCommand):
    help = 'Displays current time'

    def handle(self, *args, **kwargs):
        print("bot ls started")
        dialog_bot.run()
