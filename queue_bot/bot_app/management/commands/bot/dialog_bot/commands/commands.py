from typing import Any
from bot_app.management.commands.bot.bot_commands.command import BotCommand
from bot_app.management.commands.bot.bot_commands.commands_exceptions import MemberNotSavedError
from bot_app.management.commands.bot.utils.server.responses import Event, UsersResponse
from bot_app.models import ChatMember, Member
from bot_app.management.commands.bot.utils.keyboard.keyboard import make_keyboard


class DialogStartCommand(BotCommand):
    """ начальная команда диалогового бота """
    def __init__(self) -> None:
        super().__init__()
    
    def start(self, event: Event, **kwargs) -> Any:
        """ 
        стартовая команда определяет какой пользователь пишет боту:
        обычный пользователь или владелец беседы
        """
        try:
            if self.__is_owner(event):
                self.api.messages.send(
                    peer_id=event.peer_id,
                    message="вы можете создать очередь",
                    keyboard=make_keyboard(
                        buttons_names=["создать очередь"]
                    )
                )
            else:
                self.api.messages.send(
                    peer_id=event.peer_id,
                    message="для вас пока нет функций"
                )
        except MemberNotSavedError:
            self.api.messages.send(
                peer_id=event.peer_id,
                message=(
                    "чтобы пользоваться функциями бота нужно быть владельцем "
                    "или участником беседы, куда добавлен бот"
                )
            )

    def __is_owner(self, event: Event) -> None:
        """ проверка является ли пользователем владельцем беседы """
        user_response: dict = self.api.users.get(user_ids=event.from_id)
        user: UsersResponse = UsersResponse(user_response)
        try:
            member: Member = Member.objects.filter(member_vk_id=user.id)[0]
            # список чатов, где пользователь является владельцем
            admin_chats: list[ChatMember] = list(ChatMember.objects.filter(
                chat_member=member,
                is_admin=True
            ))
            return len(admin_chats) > 0
        except IndexError:
            """ 
            если выброшена IndexError, то пользователя нет в бд.
            это означает, что пользователя нет ни в одной беседе, где есть бот.
            """
            raise MemberNotSavedError()
