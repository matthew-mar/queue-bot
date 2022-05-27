""" Команда django для запуска бота-обрабочитка событий из личных сообщений """


from django.core.management.base import BaseCommand
from bot_app.management.commands.bot.dialog_bot.dialog_bot import dialog_bot


class Command(BaseCommand):
    help = 'Displays current time'

    def handle(self, *args, **kwargs):
        print("dialog bot started")
        dialog_bot.run()
