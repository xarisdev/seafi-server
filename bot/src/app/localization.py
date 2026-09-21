MESSAGES = {
    "reg_error": "Необходима авторизация. /start",
    "web_error": "Произошла сетевая ошибка.\n\nПопробуйте еще раз позднее или обратитесь в поддержку: @xarisssupport\n\nDetail: --detail",

    "language": {
        "message": "Выберите язык\n___\nSelect language",
        "btn_lang_ru": "Русский RU",
        "btn_lang_kg": "Кыргызча KG",
        "btn_lang_en": "English EN",
    },
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

def get_reg_error() -> str: return MESSAGES.get("reg_error")
def get_web_error() -> str: return MESSAGES.get("web_error")

def get_lang(key: str) -> str:
    """
    Text key format: `message/btn_lang_code`

    Supported code's: `ru`, `-`, `-`
    """
    data: dict = MESSAGES.get("language")
    text = data.get(key)
    return text

def get_text(key: str, lang: str = "ru") -> str:
    """
    Supported language: `ru`, `-`, `-`\n
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