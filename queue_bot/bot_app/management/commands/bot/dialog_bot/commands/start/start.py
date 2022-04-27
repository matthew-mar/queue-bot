import django
django.setup()

from ..command import BotCommand
from ....utils.bot_utils import VkApiMethods
from ...utils import is_owner
from ....utils.keyboard.keyboard import make_keyboard


class StartCommand(BotCommand):
    """
    стартовая команда, наследуется от базовго абстрактного класса BotCommand
    """
    def __init__(self, api: VkApiMethods) -> None:
        super().__init__(api)
    

    def start(self, event) -> None:
        """
        стартовая команда.

        определяет какой пользователь пишет боту - обычный или владелец беседы.

        в соответствии от типа пользвоателя отправляется соответствующее сообщение.

        входные данные:
        event: событие с VkLongPoll сервера, с информацией о текущем событии
        """
        if is_owner(user_id=event.user_id, peer_id=event.peer_id):
            self.api.messages.send(
                peer_id=event.peer_id,
                message="вы можете создать очередь для своей беседы",
                keyboard=make_keyboard(
                    default_color="primary",
                    buttons_names=["создать очередь"]
                )
            )
        else:
            self.api.messages.send(
                peer_id=event.peer_id,
                message="для вас пока нет функций"
            )
