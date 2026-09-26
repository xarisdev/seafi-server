from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from json import dumps
from .localization import localization

def generate_btn(text: str, action: str) -> InlineKeyboardButton:
    button = InlineKeyboardButton(
        text=text,
        callback_data=dumps({"data": action})
    )
    return button

def setup_keyboard(buttons: list[list[InlineKeyboardButton]]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(buttons)
    return keyboard

def get_language_keyboard():
    buttons_data = [
        {"action": "lang_ru"},
        {"action": "lang_kg"},
        {"action": "lang_en"}
    ]
    keyboard = [
        [
            InlineKeyboardButton(
                text=localization.get_lang_selector_btn(f"btn_{btn.get('action')}"),
                callback_data=dumps({"data": btn.get('action')})
            )
        ]
        for btn in buttons_data
    ]
    return InlineKeyboardMarkup(keyboard)

def get_menu_keyboard(lang: str = "ru"):
    buttons_data = [
        {"action": "sub_info"},
        {"action": "set_filter"},
        {"action": "view_prof"}
    ]
    keyboard = [
        [
            InlineKeyboardButton(
                text=localization.get(f"buttons.{btn.get('action')}", lang_code=lang),
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
                text=localization.get(f"buttons.{btn.get('action')}", lang_code=lang),
                callback_data=dumps({"data": btn.get('action')})
            )
        ]
        for btn in buttons_data
    ]
    return InlineKeyboardMarkup(keyboard)

def get_subs_keyboard(
    buttons_data: list[dict],
    lang: str = "ru"
):
    keyboard = [
        [
            InlineKeyboardButton(text=localization.get(f""))
        ]
    ]