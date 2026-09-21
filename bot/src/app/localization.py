MESSAGES = {
    "ru": {
        "welcome": "Добро пожаловать!",
        "menu": "Меню:",

        # Кнопки клавиатуры
        "buttons": {
            "sub_info": "Подписка",
            "set_filter": "Настроить фильтр",
            "view_prof": "Профиль",
            "set_menu": "В меню"
        },

        # Шаблоны для вставки
        "formats": {
            "profile": "Профиль\nID: --id\nUsername: --username\nСоздан: --created_at"
        },

        # Шаблон для объявлений
        "ads": {
            "": ""
        }
    }
}

def get_text(key: str, lang: str = "ru") -> str:
    """
    Supported language: `RU`\n
    Text key format: `"key1-key2-key3-..."`

    ### Fixed keys (key1)
    - Welcome msg - `'welcome'`
    - Menu msg - `'menu'`
    - Buttons dict key - `'buttons'`
    - Formats dict key - `'formats'`
    - Ads dict key - `'ads'`
    """
    keys = key.split("-")

    message = MESSAGES.get(lang)
    for key in keys:
        if not key:
            continue

        try:
            message = message.get(key)
        except TypeError, AttributeError:
            return f"[Missing key: {key}]"

    if isinstance(message, str):
        return message

    return f"[Key sequence incomplete: {key}]"