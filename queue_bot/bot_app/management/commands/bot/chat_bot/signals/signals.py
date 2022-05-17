from bot_app.management.commands.bot.bot_signals.signal import Signal
from bot_app.management.commands.bot.vk_api.keyboard.keyboard import make_keyboard
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
        queue: Queue = Queue.objects.filter(id=self.queue_id)[0]
        message: str = (
            "в вашей беседе появилась очередь {queue_name}\n"
            "очередь начнет работать {queue_datetime} в {queue_start_time}\n"
            .format(
                queue_name=queue.queue_name, 
                queue_datetime=self.queue_datetime,
                queue_start_time=self.queue_start_time
            )
        )
        if self.members_saved:
            message += (
                "все пользователи добавлены в очередь\n"
                "во время начала очереди вам будут приходить уведомления о "
                "вашей позиции в очереди"
            )
            keyboard = ""
        else:
            message += (
                "вы можете начать записываться в очередь"
            )
            queues: list[str] = list(map(
                lambda queue_chat: f"записаться в {queue_chat.queue.queue_name} - {queue_chat.queue.id}",
                QueueChat.objects.filter(chat=Chat.objects.filter(chat_vk_id=self.chat_id)[0])
            ))
            keyboard = make_keyboard(
                inline=False,
                buttons_names=queues
            )

        self.api.messages.send(
            peer_id=self.chat_id,
            message=message,
            keyboard=keyboard
        )
