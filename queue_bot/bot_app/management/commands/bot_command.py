from django.core.management.base import BaseCommand
from django.utils import timezone

from django.conf import settings
import django


# settings.configure()

django.setup()

from ...models import Member
from .bot.bot import main

class Command(BaseCommand):
    help = 'Displays current time'

    def handle(self, *args, **kwargs):
        print(Member.objects.all())
        main()