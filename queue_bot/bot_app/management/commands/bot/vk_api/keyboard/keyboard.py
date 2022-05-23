import json
from pprint import pprint
from datetime import datetime, timedelta


THIS_DIR = "/".join(__file__.split("/")[:-1])


def get_button() -> dict:
    with open(f"{THIS_DIR}/button_template.json") as button_template:
        return json.loads(button_template.read())


def get_keyboard() -> dict:
    with open(f"{THIS_DIR}/keyboard_template.json") as keyboard_template:
        return json.loads(keyboard_template.read())


def test_keyboard() -> str:
    with open(f"{THIS_DIR}/test_template.json") as test_temp:
        return test_temp.read()


class Button:
    def __init__(self,
        label: str,
        color: str = "secondary",
        payload: dict = {}) -> None:
        """ создание кнопки """
        self.label: str = label
        self.color: str = color
        self.payload: str = json.dumps(payload)
    
    def create_button(self) -> dict:
        button_template: dict = get_button()
        button_template["action"]["label"] = self.label
        button_template["action"]["payload"] = self.payload
        button_template["color"] = self.color
        return button_template
    
    @property
    def button_json(self) -> dict:
        button: dict = self.create_button()
        return button


def make_keyboard(
    buttons: list[Button],
    one_time: bool = False,
    inline: bool = True) -> str:
        """
        функция делает клавиатуру из пользовательских кнопок
        """
        if len(buttons) == 0:
            raise ValueError("список buttons пустой, список должен "
                "содержать как минимум один элемент"
            )
        
        keyboard: dict = get_keyboard()
        keyboard["one_time"] = one_time
        keyboard["inline"] = inline

        for i in range(0, len(buttons), 2):
            keyboard["buttons"].append(buttons[i:i+2])
        
        return json.dumps(keyboard)   


if __name__ == "__main__":
    buttons = []

    week_days = {
        0: "понедельник",
        1: "вторник",
        2: "среда",
        3: "четверг",
        4: "пятница",
        5: "суббота",
        6: "воскрессенье"
    }
    
    today = datetime.today()

    week_buttons = []
    for i in range(7):
        date = today + timedelta(days=i)
        week_buttons.append(Button(
            label=week_days[date.weekday()],
            payload={
                "button_type": "week_day",
                "date": {
                    "day": date.day,
                    "month": date.month,
                    "year": date.year
                }
            }
        ).button_json)
    
    pprint(week_buttons)
