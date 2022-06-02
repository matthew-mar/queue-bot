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


class Button:
    def __init__(self, label: str, color: str = "primary", payload: dict = {}) -> None:
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


def make_keyboard(buttons: list[Button], one_time: bool = False, inline: bool = True) -> str:
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
