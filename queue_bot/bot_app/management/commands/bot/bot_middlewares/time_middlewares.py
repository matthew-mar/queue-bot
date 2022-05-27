from datetime import date, datetime


def get_date(date: dict) -> datetime:
    """
    Возвращает объект datetime вида datetime(xxxx, x, x)

    :date (dict)
        словарь с ключами year, month, day
    """
    return datetime(
        year=date["year"],
        month=date["month"],
        day=date["day"]
    )


def get_datetime(time_string: str, date: datetime) -> tuple:
    """
    Получает строку со временем в формате "hh:mm" и возвращает кортеж,
    где первый элемент - это часы, воторой - минуты.
    
    :time_string (str)
        время.

    :date (datetime)
        день начала очереди. Нужен для того, чтобы нельзя было ввести
        прошедшее время сегодняшнего дня.
    """
    hours, minutes = map(int, time_string.split(":"))
    
    begin_hour = 0
    begin_minutes = 0

    if date.day == datetime.now().day:  # если день очереди сегодня
        begin_hour = datetime.now().hour
        begin_minutes = datetime.now().minute

        # return date.replace(hour=hours, minute=minutes)

    print("queue hours", hours, "begin hour", begin_hour)
    print("queue minutes", minutes, "begin minutes", begin_minutes)

    if (hours < 23) and (hours > begin_hour):
        if (minutes < 60) and (minutes >= 0):
            return date.replace(hour=hours, minute=minutes)
        else:
            raise ValueError
    elif (hours == begin_hour):
        if (minutes < 60) and (minutes >= begin_minutes):
            return date.replace(hour=hours, minute=minutes)
        else:
            raise ValueError
    else:
        raise ValueError


def dates_equal(date_1: datetime, date_2: datetime) -> bool:
    """
    Сравнение двух дат

    :date_1 (datetime)
        первая дата
    
    :date_2 (datetime)
        вторая дата

    Даты приводятся к общему формату "%Y.%m.%d %H:%M" и сравниваются строки.
    """
    return date_1.strftime("%Y.%m.%d %H:%M") == date_2.strftime("%Y.%m.%d %H:%M")
