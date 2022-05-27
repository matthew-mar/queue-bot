from bot_app.management.commands.bot.vk_api.vk_api import Session, VkApiMethods

from bot_app.management.commands.bot.vk_api.longpoll.responses import (
    ConversationsResponse, MembersResponse, UserResponse)


vk_api: VkApiMethods = Session().api


def get_chat_members(peer_id: int) -> MembersResponse:
    """
    Получение участников беседы

    :peer_id (int)
        peer_id беседы.
    """
    return MembersResponse(
        members=vk_api.messages.get_conversation_members(
            peer_id=peer_id
        )
    )


def get_user(user_id: int) -> UserResponse:
    """
    Получение данных о пользователе

    :user_id (int)
        vk_id пользователя.
    """
    return UserResponse(user_response=vk_api.users.get(user_ids=user_id))


def get_conversation(peer_id: int) -> ConversationsResponse:
    """
    Получение информации о беседе

    :peer_id (int)
        peer_id беседы.
    """
    return ConversationsResponse(
        conversations=vk_api.messages.get_conversations_by_id(peer_id)
    )
