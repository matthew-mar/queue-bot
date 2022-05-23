from typing import Any
from bot_app.management.commands.bot.vk_api.vk_api import Session, VkApiMethods
from abc import ABC
from bot_app.management.commands.bot.vk_api.longpoll.responses import Event


class BotCommand(ABC):
    """
    абстрактный клаcc, описывающий работу команды бота
    """

    @staticmethod
    def new_call(event: Event, current_step: dict) -> bool:
        """ 
        определяет является ли вызов команды новым вызовом 
        
        :event (Event) - событие с longpoll сервера
        :current_step (dict) - словарь, хранящий текущее состояние команды для пользователя

        если в словаре current_step нет id пользователя, тогда команда вызвана
        этим пользователем в первый раз.
        """
        return event.from_id not in current_step

    def __init__(self) -> None:
        self.api: VkApiMethods = Session().api  # получение доступа к vk_api
        self.command_ended: bool = False  # контроль завершения команды
        # текущее действие команды (ипользуется если команда работает в несколько действий)
        self.current_step: dict = {}
    
    def start(self, event: Event, **kwargs) -> Any:
        """
        точка входа в команду. начало действий команды

        входные параметры:
        :event - событие с VkLongPoll сервера
        """
        self.command_ended = False
        if self.new_call(event, self.current_step):  # если новый вызов
            # определяем начальное действие
            self.current_step[event.from_id] = self.start_action
        
        # получение текущего действия для пользователя
        current_step_method = self.current_step[event.from_id]
        current_step_method(event)  # вызов метода
    
    def start_action(self, event: Event) -> None: 
        """ начальное действие команды """
        return None

    def next_step(self, from_id: int, step_method) -> None:
        """ 
        переход к следующему шагу команды 
        
        :from_id (int) - id пользователя, который выполняет команду
        :step_method - метод для следующего шага команды
        """
        self.current_step[from_id] = step_method

    def go_next(self, event: Event, next_method, next_step) -> None:
        """
        выполнение действий перед переходом к следующему шагу команды

        :event (Event) - событие с longpoll сервера
        :next_method - метод, который нужно выполнить перед переходом к следующему шагу
        :next_step - метод следующего шага команды
        """
        next_method(event)
        self.next_step(from_id=event.from_id, step_method=next_step)

    def end(self, event: Event) -> None:
        """ завершение команды """
        self.current_step.pop(event.from_id)
        self.command_ended = True
