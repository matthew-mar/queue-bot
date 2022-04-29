from bot_app.management.commands.bot.dialog_bot.commands.command import BotCommand
from bot_app.management.commands.bot.utils.utils import is_owner
from bot_app.management.commands.bot.utils.keyboard.keyboard import make_keyboard
from bot_app.management.commands.bot.utils.api import Api


class StartCommand(BotCommand):
    """
    стартовая команда, наследуется от базовго абстрактного класса BotCommand
    """
    def __init__(self) -> None:
        self.api: Api = Api()

    def start(self, event) -> None:
        """
        стартовая команда.

        определяет какой пользователь пишет боту - обычный или владелец беседы.

        в соответствии от типа пользвоателя отправляется соответствующее сообщение.

        входные данные:
        event: событие с VkLongPoll сервера, с информацией о текущем событии
        """
        if is_owner(user_id=event.user_id, peer_id=event.peer_id):
            self.api.methods.messages.send(
                peer_id=event.peer_id,
                message="вы можете создать очередь для своей беседы",
                keyboard=make_keyboard(
                    default_color="primary",
                    buttons_names=["создать очередь"]
                )
            )
        else:
            self.api.methods.messages.send(
                peer_id=event.peer_id,
                message="для вас пока нет функций"
            )
