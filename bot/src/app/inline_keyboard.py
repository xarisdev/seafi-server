from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from json import dumps
from .localization import get_text

def get_menu_keyboard(lang: str = "ru"):
    buttons_data = [
        {"action": "sub_info"},
        {"action": "set_filter"},
        {"action": "view_prof"}
    ]
    keyboard = [
        [
            InlineKeyboardButton(
                text=get_text(f"buttons-{btn.get('action')}", lang=lang),
                callback_data=dumps({"data": btn.get('action')})
            )
        ]
        for btn in buttons_data
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_menu(lang: str = "ru"):
    buttons_data = [
        {"action": "set_menu"}
    ]
    keyboard = [
        [
            InlineKeyboardButton(
                text=get_text(f"buttons-{btn.get('action')}", lang=lang),
                callback_data=dumps({"data": btn.get('action')})
            )
        ]
        for btn in buttons_data
    ]
    return InlineKeyboardMarkup(keyboard)

if __name__ == "__main__":
    print(get_menu_keyboard().to_dict())