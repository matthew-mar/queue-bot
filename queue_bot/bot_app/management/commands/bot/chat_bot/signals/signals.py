import json
from bot_app.management.commands.bot.bot_middlewares.db_middlewares import get_queue_by_id, get_queue_order
from bot_app.management.commands.bot.bot_middlewares.keyboard_middlewares import queue_enroll_buttons
from bot_app.management.commands.bot.bot_signals.signal import Signal
from bot_app.management.commands.bot.dialog_bot.messages import NewQueueSignalMessages
from bot_app.management.commands.bot.vk_api.keyboard.keyboard import Button, make_keyboard
from bot_app.management.commands.bot.vk_api.longpoll.responses import UserResponse
from bot_app.management.commands.bot.vk_api.vk_api import Users
from bot_app.models import Chat, Queue, QueueChat


class NewQueueSignal(Signal):
    """ сигнал сохранения новой очереди """
    def __init__(self, signal_name: str, args: dict) -> None:
        super().__init__(signal_name, args)
        self.chat_id: int = args.get("chat_id")
        self.queue_id: int = args.get("queue_id")
        self.queue_datetime: str = args.get("queue_day")
        self.queue_start_time: str = args.get("queue_start_time")
        self.members_saved: bool = args.get("members_saved")
    
    def execute(self) -> None:
        queue: Queue = get_queue_by_id(queue_id=self.queue_id)
        message: str = NewQueueSignalMessages.NEW_QUEUE_MESSAGE.format(
            queue_name=queue.queue_name, 
            queue_datetime=self.queue_datetime,
            queue_start_time=self.queue_start_time
        )
        if self.members_saved:
            message += NewQueueSignalMessages.MEMBERS_SAVED_MESSAGE.format(
                get_queue_order(queue.queue_members)
            )
            keyboard = ""
        else:
            message += NewQueueSignalMessages.START_ENROLL_MESSAGE
            keyboard = make_keyboard(
                inline=False,
                buttons=queue_enroll_buttons(peer_id=self.chat_id)
            )

        self.api.messages.send(
            peer_id=self.chat_id,
            message=message,
            keyboard=keyboard
        )
