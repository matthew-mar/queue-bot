from bot_app.management.commands.bot.bot_signals.signal import Signal
from bot_app.management.commands.bot.bot_middlewares.db_middlewares import first_in_queue, get_chat_by_queue, get_member_order, get_queue_by_id
from bot_app.management.commands.bot.dialog_bot.messages import QueueEnrollMessages
from bot_app.management.commands.bot.bot_middlewares.keyboard_middlewares import dialog_standart_buttons
from bot_app.management.commands.bot.vk_api.keyboard.keyboard import make_keyboard
from bot_app.management.commands.bot.bot_commands.commands_exceptions import QueueEmptyError


class QueueEnrollFromChatSignal(Signal):
    def __init__(self, signal_name: str, args: dict) -> None:
        super().__init__(signal_name, args)
        self.user_id: int = args.get("user_id")
        self.queue_id: int = args.get("queue_id")
        self.member_in_queue: bool = args.get("member_in_queue")

    def execute(self) -> None:
        queue = get_queue_by_id(queue_id=self.queue_id)
        if self.member_in_queue:
            message = QueueEnrollMessages.ALREADY_IN_QUEUE_MESSAGE.format(
                get_member_order(
                    queue=queue,
                    user_id=self.user_id
                )
            )
        else:
            message = QueueEnrollMessages.QUEUE_ENROLLED_MESSAGE.format(
                queue.queue_name, 
                get_chat_by_queue(queue),
                get_member_order(queue=queue, user_id=self.user_id)
            )
        self.api.messages.send(
            peer_id=self.user_id,
            message=message,
            keyboard=make_keyboard(
                inline = False,
                buttons=dialog_standart_buttons
            )
        )


class NextInQueueSignal(Signal):
    def __init__(self, signal_name: str, args: dict) -> None:
        super().__init__(signal_name, args)
        self.queue_id: int = args.get("queue_id")
    
    def execute(self) -> None:
        queue = get_queue_by_id(queue_id=self.queue_id)
        chat = get_chat_by_queue(queue=queue)
        message = "вы следующий в очереди {} из беседы {}".format(queue.queue_name, chat.chat_name)
        try:
            self.api.messages.send(
                peer_id=first_in_queue(queue_id=self.queue_id),
                message=message,
                keyboard=make_keyboard(
                    inline = False,
                    buttons=dialog_standart_buttons
                )
            )
        except QueueEmptyError:
            queue.delete()
