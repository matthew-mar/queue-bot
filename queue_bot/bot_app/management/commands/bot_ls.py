from django.core.management.base import BaseCommand
from django.utils import timezone

from .bot import test_bot

class Command(BaseCommand):
    help = 'Displays current time'

    def handle(self, *args, **kwargs):
        print("bot ls started")
        test_bot.run()
