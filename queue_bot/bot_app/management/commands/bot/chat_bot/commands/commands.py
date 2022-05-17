import json
from pprint import pprint
from typing import Any
from bot_app.management.commands.bot.bot_commands.command import BotCommand
from bot_app.management.commands.bot.bot_commands.commands_exceptions import ChatAlreadySavedError
from bot_app.management.commands.bot.vk_api.longpoll.responses import ConversationsResponse, Event, MembersResponse, Profile, UsersResponse
from bot_app.management.commands.bot.vk_api.keyboard.keyboard import make_keyboard
from bot_app.models import Chat, ChatMember, Member, Queue, QueueChat


class ChatInvitationCommand(BotCommand):
    """ команда приглашения в беседу """
    def __init__(self) -> None:
        super().__init__()
    
    def start(self, event: Event, **kwargs) -> Any:
        self.api.messages.send(
            peer_id=event.peer_id,
            message=(
                "чтобы пользоваться моими функциями сделайте меня администратором "
                "и нажмите кнопку \"start\""
            ),
            keyboard=make_keyboard(
                inline=False,
                buttons_names=["start"]
            )
        )


class ChatStartCommand(BotCommand):
    """ команда "start" в беседеах """
    def __init__(self) -> None:
        super().__init__()

    def start(self, event: Event, **kwargs) -> Any:
        # получение информации о беседе
        conversations: dict = self.api.messages.get_conversations_by_id(event.peer_id)
        conversation_response: ConversationsResponse = ConversationsResponse(conversations=conversations)
        if self.__is_admin(conversation_response):
            try:
                # сохранение чата
                chat: Chat = self.__save_chat(conversation_response)

                # получение информации об участниках беседы
                members: dict = self.api.messages.get_conversation_members(peer_id=event.peer_id)
                members_response: MembersResponse = MembersResponse(members=members)
                # соханение участников
                members: list[Member] = self.__members_save(members_response)

                # сохранение связи между беседой и участниками
                self.__chat_members_connection(chat, members_response.profiles, conversation_response)

                self.api.messages.send(
                    peer_id=event.peer_id,
                    message=(
                        "ваша беседа успешно сохранена, теперь вы можете "
                        "создавать очереди"
                    )
                )
            except ChatAlreadySavedError as exception:
                self.api.messages.send(
                    peer_id=event.peer_id,
                    message=exception.args[0]
                )
        else:
            self.api.messages.send(
                peer_id=event.peer_id,
                message="сделайте бота администратором и повторите попытку"
            )

    def __is_admin(self, conversation_response: ConversationsResponse) -> bool:
        """ проверка, является ли бот админом в беседе """
        return conversation_response.count > 0
    
    def __save_chat(self, conversation_response: ConversationsResponse) -> Chat:
        """ сохранение чата в бд """
        try:
            Chat.objects.filter(chat_vk_id=conversation_response.peer_id)[0]
            raise ChatAlreadySavedError(f"беседа {conversation_response.title} уже сохранена")
        except IndexError:
            """ если выбрасывается IndexError значит беседы нет в бд """
            # инициализация полей новой беседы
            chat_name: str = conversation_response.title
            chat_vk_id: int = conversation_response.peer_id
            # новая запись в бд
            chat: Chat = Chat(chat_name=chat_name, chat_vk_id=chat_vk_id)
            chat.save()
            print(f"беседа {chat_name} сохранена")
            return chat
    
    def __members_save(self, members_response: MembersResponse) -> list[Member]:
        """ сохранение участников беседы """
        # список vk_id пользователей, сохраненных в бд
        members_vk_ids: list[int] = [
            int(member.member_vk_id)
            for member in Member.objects.all()
        ]
        # список профилей участников беседы
        profiles: list[Profile] = members_response.profiles

        members: list[Member] = []

        for member in profiles:
            if member.user_id not in members_vk_ids:
                new_member: Member = Member(
                    member_vk_id=member.user_id,
                    name=member.first_name,
                    surname=member.last_name
                )
                new_member.save()
                members.append(new_member)
                print("пользователь {name} {surname} сохранен".format(
                    name=member.first_name,
                    surname=member.last_name
                ))
        
        return members
    
    def __chat_members_connection(self, 
        chat: Chat, 
        profiles: list[Profile],
        conversation_response: ConversationsResponse) -> None:
        """ сохранение в бд связи между беседой и участниками беседы """
        members: list[Member] = [  # список участников беседы, сохраненных в бд
            Member.objects.filter(
                member_vk_id=member.user_id,
                name=member.first_name,
                surname=member.last_name
            )[0]
            for member in profiles
        ]
        for member in members:  # сохранение участников
            ChatMember(
                chat=chat,
                chat_member=member,
                is_admin=(int(member.member_vk_id) == conversation_response.owner_id)
            ).save()


class CickUserCommand(BotCommand):
    """ команда удаления пользователя из беседы """
    def __init__(self) -> None:
        super().__init__()
    
    def start(self, event: Event, **kwargs) -> Any:
        """ удаление связи между пользователем и беседой """
        kicked_member: Member = Member.objects.filter(
            member_vk_id=event.action["member_id"]
        )[0]
        chat: Chat = Chat.objects.filter(
            chat_vk_id=event.peer_id
        )[0]
        chat_member: ChatMember = ChatMember.objects.filter(
            chat_member=kicked_member,
            chat=chat
        )[0]
        chat_member.delete()


class InviteUserCommand(BotCommand):
    """ команда добавления пользоателя """
    def __init__(self) -> None:
        super().__init__()

    def start(self, event: Event, **kwargs) -> Any:
        """ создание связи между новым пользователем и беседой """
        if not event.action_from_bot:
            try:
                new_member: Member = Member.objects.filter(
                    member_vk_id=event.action["member_id"]
                )[0]
            except IndexError:
                """ 
                если выброшена IndexError то пользователя с таким id 
                нет в бд. Значит пользователя нужно сохранить
                """
                member_response: UsersResponse = UsersResponse(self.api.users.get(event.action["member_id"]))
                new_member: Member = Member(
                    member_vk_id=member_response.id,
                    name=member_response.first_name,
                    surname=member_response.last_name
                ).save()
            finally:
                chat: Chat = Chat.objects.filter(
                    chat_vk_id=event.peer_id
                )[0]
                ChatMember(
                    chat=chat,
                    chat_member=new_member,
                    is_admin=False
                ).save()


class QueueEnrollCommand(BotCommand):
    """ команда записи в очередь """
    def __init__(self) -> None:
        super().__init__()
    
    def start(self, event: Event, **kwargs) -> Any:
        print(event.text)
        queue_id: int = int(event.text.split()[-1])
        queue: Queue = Queue.objects.filter(id=queue_id)[0]
        members: list[dict] = json.loads(queue.queue_members)
        members_ids = list(map(lambda member: member["member"], members))
        print(members_ids)
        if event.from_id not in members_ids:
            members.append({
                "member": event.from_id
            })
            queue.queue_members = json.dumps(members)
            queue.save()
            print("saved")
        print(members)
        # queues: list[str] = list(map(
        #         lambda queue_chat: f"записаться в {queue_chat.queue.queue_name}",
        #         QueueChat.objects.filter(chat=Chat.objects.filter(chat_vk_id=self.chat_id)[0])
        #     ))
