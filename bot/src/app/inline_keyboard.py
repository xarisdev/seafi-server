import json
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def get_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("Подписка", callback_data=json.dumps({"a": "sub_info"}))],
        [InlineKeyboardButton("Настроить фильтр", callback_data=json.dumps({"a": "set_filter"}))],
        [InlineKeyboardButton("Профиль", callback_data=json.dumps({"a": "view_prof"}))]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_menu():
    keyboard = [[InlineKeyboardButton("В меню", callback_data=json.dumps({"a": "set_menu"}))]]
    return InlineKeyboardMarkup(keyboard)