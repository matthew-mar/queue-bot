from datetime import datetime, timedelta
from bot_app.management.commands.bot.bot_middlewares.db_middlewares import get_chat
from bot_app.management.commands.bot.vk_api.keyboard.keyboard import Button
from bot_app.management.commands.bot.bot_middlewares.middlewares import get_week_day
from bot_app.models import ChatMember, Queue, QueueChat


def days_buttons():
    today = datetime.today()

    week_buttons = []
    for i in range(7):
        date = today + timedelta(days=i)
        week_buttons.append(Button(
            label=get_week_day(day=date.weekday()),
            payload={
                "button_type": "week_day",
                "date": {
                    "day": date.day,
                    "month": date.month,
                    "year": date.year
                }
            }
        ).button_json)

    return week_buttons


dialog_standart_buttons: list[Button] = [  # стандартная клавиатура
    Button(label="создать очередь").button_json,
    Button(label="записаться в очередь").button_json,
    Button(label="удалиться из очереди").button_json,
    Button(label="получить место в очереди").button_json
]


make_chat_button = lambda chat_member: Button(
    label=chat_member.chat.chat_name,
    payload={
        "button_type": "chat_name_button",
        "chat_id": chat_member.chat.chat_vk_id
    }
).button_json


yes_no_buttons: list[dict] = list(map(
    lambda choice: Button(label=choice).button_json,
    ("да", "нет")
))


def chat_buttons(chats_members: list[ChatMember]) -> list[Button]:
    """
    функция делает кнопки с названиями чатов

    :chats_members (list[ChatMember]) - список связей между беседами и участниками
    """
    return list(map(
        make_chat_button,
        chats_members
    ))


def queues_buttons(queues: list[list[Queue]]) -> list[Button]:
    """
    функция делает кнопки с названием бесед

    :queues - двумерный список с очередями
    """
    buttons = []
    for queue_list in queues:
        buttons.extend(list(map(
            lambda queue: Button(label=queue.queue_name, payload={
                "button_type": "queue_enroll_button",
                "queue_id": queue.id
            }).button_json,
            queue_list
        )))
    return buttons


def queues_delete_buttons(queues: list[Queue]) -> list[Button]:
    """
    функция делает кнопки с названием очередей

    :queues - двумерный список с очередями
    """
    return list(map(
        lambda queue: Button(label=queue.queue_name, payload={
            "button_type": "queue_delete_button",
            "queue_id": queue.id
        }).button_json,
        queues
    ))


def queues_order_buttons(queues: list[Queue]) -> list[Button]:
    """
    функция делает кнопки с названием бесед

    :queues - двумерный список с очередями
    """
    return list(map(
        lambda queue: Button(label=queue.queue_name, payload={
            "button_type": "queue_order_button",
            "queue_id": queue.id
        }).button_json,
        queues
    ))


def queue_enroll_buttons(peer_id: int) -> list[Button]:
    """
    функция делает кнопки для записи в очередь
    
    :peer_id (int) - peer_id беседы
    """
    return list(map(
        lambda queue_chat: Button(
            label=f"записаться в {queue_chat.queue.queue_name}",
            payload={
                "button_type": "queue_enroll_button",
                "queue_id": queue_chat.queue.id
            }).button_json,
        QueueChat.objects.filter(chat=get_chat(vk_id=peer_id))
    ))
