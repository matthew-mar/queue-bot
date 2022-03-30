from django.core.management.base import BaseCommand
from django.utils import timezone

from .bot import bot

class Command(BaseCommand):
    help = 'Displays current time'

    def handle(self, *args, **kwargs):
        print("bot started")        
        bot.start()
