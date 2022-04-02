import django
django.setup()

from pprint import pprint
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType
from .utils.bot_utils import read_token, VkApiMethods
from .utils.keyboard.keyboard import make_keyboard
from ....models import Member, ChatMember


# авторизация
session: VkApi = VkApi(token=read_token())
api_methods: VkApiMethods = VkApiMethods(session.get_api())


def is_user_saved(user_id: int) -> bool:
    """
    функция проверяет сохранен ли пользователь в бд

    входные данные:
    user_id (int): vk id пользвателя, который отправил сообщение.

    выходные данные:
    возвращает True, если пользователь есть в бд и False, если его нет.
    """
    try:
        # попытка получения пользователя из бд
        user: Member = Member.objects.filter(member_vk_id=user_id)[0]
        return True
    except IndexError:
        """
        если выбрасывается IndexError - пользователя с таким id нет в бд.
        """
        return False


def is_owner(user_id: int) -> bool:
    """
    функция определяет является ли пользователь владельцем беседы.

    входные данные:
    user_id (int): vk id пользвателя, который отправил сообщение.

    выходные данные:
    возвращает True, если пользователь является владельцем, и False нет.
    """
    user: Member = Member.objects.filter(member_vk_id=user_id)[0]
    chat_member: ChatMember = ChatMember.objects.filter(chat_member=user)[0]
    return chat_member.is_admin


def start_command(user_id: int, peer_id: int):
    """
    функция стартовой команды.

    осуществляет начало работы с ботом.
    функция определяет сохранен ли пользователь в бд.
    затем функция определяет является ли пользовтель владельцем беседы.
    в зависимости от этого предоставляет доступ к определенному функционалу.
    
    входные данные:
    user_id (int): vk id пользвателя, который отправил сообщение.

    peer_id (int): vk id диалога, в котором происходит общение.
    """
    if is_user_saved(user_id=user_id):
        if is_owner(user_id=user_id):
            api_methods.messages.send(
                peer_id=peer_id,
                message="Вы можете создать очередь для своей беседы",
                keyboard=make_keyboard(**{
                    "buttons_names": ["создать очередь"],
                    "buttons_colors": ["primary"]
                })
            )
        else:
            api_methods.messages.send(
                peer_id=peer_id,
                message="пока вы ничего не можете сделать"
            )
    else:
        api_methods.messages.send(
            peer_id=peer_id,
            message="Чтобы пользоваться функциями бота вы должны быть в одной из бесед, где есть бот"
        )


def run():
    longpoll: VkLongPoll = VkLongPoll(session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            message_text: str = event.text.lower()
            if message_text == "начать":
                start_command(user_id=event.user_id, peer_id=event.peer_id)
