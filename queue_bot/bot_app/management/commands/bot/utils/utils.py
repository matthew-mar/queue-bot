from bot_app.models import Member, ChatMember


def is_owner(user_id: int, peer_id: int) -> bool:
    """
    определяет является ли пользвоатель владельцем беседы

    входные параметры:
    user_id (int): vk id пользователя

    peer_id (int): vk id чата, для отправления сообщения об ошибке

    выходные данные:
    True - если пользвоатель является владельцем
    False - если не является
    """
    try:
        # получение пользователя из бд по user_id
        user: Member = Member.objects.filter(member_vk_id=user_id)[0]
        # получение всех полей с пользователем, где он является админом беседы
        chats_members = ChatMember.objects.filter(
            chat_member=user,
            is_admin=True
        )
        # если длина QuerySet больше 0, то такие беседы есть, иначе нет
        return len(chats_members) > 0
    except IndexError:
        """
        если выбрасывается IndexError - то пользователя не существует в бд.
        """
        # api_methods.messages.send(
        #     peer_id=peer_id,
        #     message="ошибка! вас нет в бд."
        # )
        return False
