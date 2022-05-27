from bot_app.management.commands.bot.vk_api.vk_api import Session, VkApiMethods
from abc import ABC
from bot_app.management.commands.bot.vk_api.longpoll.responses import Event


class BotCommand(ABC):
    """
    Абстрактный клаcc BotCommand, описывает работу команды бота
    """

    @staticmethod
    def new_call(event: Event, current_step: dict) -> bool:
        """ 
        Определяет является ли вызов команды новым вызовом, возвращает True
        или False.
        
        :event (Event)
            событие с longpoll сервера.
        
        :current_step (dict)
            словарь, хранящий текущее состояние команды для пользователя.

        Если в словаре current_step нет id пользователя, тогда команда вызвана
        этим пользователем в первый раз.
        """
        return event.from_id not in current_step

    def __init__(self) -> None:
        self.api: VkApiMethods = Session().api  # получение доступа к vk_api
        self.command_ended: bool = False  # контроль завершения команды
        # текущее действие команды (ключи - vk_id пользователей)
        self.current_step: dict = {}
    
    def start(self, event: Event) -> None:
        """
        Точка входа в команду.
        
        :event (Event)
            событие с VkLongPoll сервера.
        """
        self.command_ended = False
        if self.new_call(event, self.current_step):
            # определяем начальное действие
            self.current_step[event.from_id] = self.start_action
        
        # получение текущего действия для пользователя
        current_step_method = self.current_step[event.from_id]
        current_step_method(event)  # вызов метода
    
    def start_action(self, event: Event) -> None: 
        """ Начальное действие команды """
        return None

    def next_step(self, from_id: int, step_method) -> None:
        """ 
        Переход к следующему шагу команды 
        
        :from_id (int)
            id пользователя, который выполняет команду.
        
        :step_method
            метод для следующего шага команды.

        Устанавливает step_method в качестве текущего действия команды.
        """
        self.current_step[from_id] = step_method

    def go_next(self, event: Event, next_method, next_step) -> None:
        """
        Выполнение действий перед переходом к следующему шагу команды

        :event (Event)
            событие с longpoll сервера.
        
        :next_method
            метод, который нужно выполнить перед переходом к следующему шагу.
        
        :next_step
            метод следующего шага команды.
        """
        next_method(event)
        self.next_step(from_id=event.from_id, step_method=next_step)

    def end(self, user_id: int) -> None:
        """ 
        Завершение команды 
        
        :user_id (int)
            vk_id пользователя.
        
        Метод удаляет пользователя из последовательности действий.
        """
        self.current_step.pop(user_id)
        self.command_ended = True
