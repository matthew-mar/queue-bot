import json
from pprint import pprint


THIS_DIR = "/".join(__file__.split("/")[:-1])


def get_button() -> dict:
    with open(f"{THIS_DIR}/button_template.json") as button_template:
        return json.loads(button_template.read())


def get_keyboard() -> dict:
    with open(f"{THIS_DIR}/keyboard_template.json") as keyboard_template:
        return json.loads(keyboard_template.read())


def make_keyboard(one_time: bool = False, default_color: str = "secondary", **kwargs) -> str:
        """
        функция делает клавиатуру из пользовательских кнопок

        входные параметры:
        buttons_names (list[str]): список с названиями кнопок. 
        не может быть пустым списокм!

        buttons_colors (list[str]): необязательный параметр список с цветами кнопок.
        цвет кнопки присваивается соответствующей по индексу кнопке из списка
        buttons_names

        default_color="secondary" (str): необязательный параметр "цвет по умолчанию".
        присваивается кнопкам, для которых не указан цвет в списке button_colors.
        по умолчанию - белый цвет.

        one_time=False (bool): необязательный параметр, который отвечает за
        количество показов кнопки. Если True, то кнопка исчезнет при нажатии.
        """
        buttons_names: list[str] = kwargs.get("buttons_names")
        if isinstance(buttons_names, type(None)):
            raise TypeError("пропущен обязательный аргумент: buttons_names")
        elif len(buttons_names) == 0:
            raise ValueError("список buttons_names пустой, список должен "
                "содержать как минимум один элемент"
            )

        buttons_colors: list[str] = kwargs.get("buttons_colors")
        if isinstance(buttons_colors, type(None)):
            buttons_colors = [default_color] * len(buttons_names)
        elif len(buttons_colors) > len(buttons_names):
            raise ValueError("значений в списке buttons_colors не может быть "
                "больше, чем в списке buttons_names"
            )
        elif len(buttons_colors) < len(buttons_names):
            for i in range(len(buttons_names) - len(buttons_colors)):
                buttons_colors.append(default_color)
        
        keyboard: dict = get_keyboard()
        keyboard["one_time"] = one_time
        for i in range(len(buttons_names)):
            button: dict = get_button()
            button["action"]["payload"] = "{\"button\": \"%d\"}" % (i + 1)
            button["action"]["label"] = buttons_names[i]
            button["color"] = buttons_colors[i]
            keyboard["buttons"][0].append(button)
        
        return json.dumps(keyboard, indent=2)   


if __name__ == "__main__":
    keyboard: str = make_keyboard(default_color="negative", **{
        "buttons_names": ["start", "add_queue"],
        "buttons_colors": ["secondary", "negative", "secondary"]
    })
    print(keyboard)
