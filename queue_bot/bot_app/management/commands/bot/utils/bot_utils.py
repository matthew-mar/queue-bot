from pprint import pprint
from week import Week
import datetime


BOT_DIR: str = "/".join(__file__.split("/")[:-1])

week_days: dict[str:int] = {  # словарь соответствий дня недели с его номером
    "понедельник": 1,
    "вторник": 2,
    "среда": 3,
    "четверг": 4,
    "пятница": 5,
    "суббота": 6,
    "воскресенье": 7
}


def read_token() -> str:
    """ функция считывает токен из файла """
    with open(f"{BOT_DIR}/token.txt") as token_file:
        token: str = token_file.read()
    return token


def get_days() -> list[str]:
    """ функция отправляет список доступных дней для пользователя """
    days: list[str] = []
    today: int = datetime.date.today().weekday() + 1
    for day in week_days:
        if week_days[day] >= today:
            days.append(day)
    return days


def get_datetime(day: int, hours: int, minutes: int) -> datetime:
    """ возвращает дату и время начала очереди """
    return datetime.datetime(
        year=int(Week.thisweek().startdate.strftime("%Y")),
        month=int(Week.thisweek().startdate.strftime("%m")),
        day=int(Week.thisweek().startdate.strftime("%d")) + day-1,
        hour=hours,
        minute=minutes
    )
