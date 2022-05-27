import requests


class BotApi:
    """ 
    Класс BotApi для взаимодействия с функциями api бота.

    Класс реализует паттерн Singleton. 
    """

    __instance = None

    __base_url = "http://127.0.0.1:8000/bot/"

    def __new__(cls) -> "BotApi":
        """ 
        Конструктор класса 
        
        В конструкторе происходит проверка на существование экземпляра BotApi.

        Экземпляр класса BotApi хранится в полне __instance.
        """
        if cls.__instance is None:
            cls.__instance = super(BotApi, cls).__new__(cls)
        return cls.__instance
    
    def send_signal(cls, to: str, data: dict) -> None:
        """
        отправляет сигнал и его аргументы на сервер

        :to (str): куда отправляется сигнал (chat/dialog)
        :data (dict): данные о сигнале
        """
        url: str = f"{cls.__base_url}{to}/"
        requests.post(url=url, data=data)
