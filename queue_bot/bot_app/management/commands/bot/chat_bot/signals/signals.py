import json
from bot_app.management.commands.bot.bot_signals.signal import Signal
from bot_app.management.commands.bot.vk_api.keyboard.keyboard import Button, make_keyboard
from bot_app.management.commands.bot.vk_api.longpoll.responses import UsersResponse
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
            queue_members: list[dict] = json.loads(queue.queue_members)
            members_ids: list[int] = list(map(
                lambda queue_member: queue_member["member"],
                queue_members
            ))
            users: list[UsersResponse] = list(map(
                lambda user_id: UsersResponse(self.api.users.get(user_id)),
                members_ids
            ))
            users_message = "\n".join(
                    list(map(
                        lambda user: "{0}. {1} {2}".format(users.index(user) + 1, user.first_name, user.last_name),
                        users
                    ))
                )
            message += (
                "все пользователи добавлены в очередь\n"
                "во время начала очереди вам будут приходить уведомления о "
                "вашей позиции в очеред\n"
                "текущий порядок очереди:\n\n"
                f"{users_message}"
            )
            keyboard = ""
        else:
            message += (
                "вы можете начать записываться в очередь"
            )
            queues: list[dict] = list(map(
                lambda queue_chat: Button(
                    label=f"записаться в {queue_chat.queue.queue_name}",
                    payload={
                        "button_type": "queue_enroll_button",
                        "queue_id": queue_chat.queue.id
                    }).button_json,
                QueueChat.objects.filter(chat=Chat.objects.filter(chat_vk_id=self.chat_id)[0]
            )))
            keyboard = make_keyboard(
                inline=False,
                buttons=queues
            )

        self.api.messages.send(
            peer_id=self.chat_id,
            message=message,
            keyboard=keyboard
        )
