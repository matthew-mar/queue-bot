from datetime import datetime


def get_datetime(queue_info: dict) -> datetime:
    """
    формирование даты и времени из словаря с информацией об очереди

    :queue_info (dict)
    """
    return datetime(
        year=queue_info["date"]["year"],
        month=queue_info["date"]["month"],
        day=queue_info["date"]["day"],
        hour=queue_info["time"][0],
        minute=queue_info["time"][1]
    )
