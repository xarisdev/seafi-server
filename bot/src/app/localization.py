import logging

from typing import Optional, Literal
from string import Template

logger = logging.getLogger(__name__)

ERRORS = {
    "reg": "Необходима авторизация. /start",
    "web": "Произошла сетевая ошибка.\n\nПопробуйте еще раз позднее или обратитесь в поддержку: @xarisssupport\n\nDetail: $detail",
}
LANGUAGES = {
    "message": "Выберите язык\n___\nSelect language",
    "btn_lang_ru": "Русский RU",
    "btn_lang_kg": "Кыргызча KG",
    "btn_lang_en": "English EN"
}
MESSAGES = {
    "ru": {
        "welcome": "Добро пожаловать!",
        "menu": "Меню:",

        # Keyboard buttons
        "buttons": {
            "sub_info": "Подписка",
            "set_filter": "Настроить фильтр",
            "view_prof": "Профиль",
            "set_menu": "В меню"
        },

        # VIEW Templates
        "templates": {
            "profile": "Профиль\nID: $id\nUsername: $username\nСоздан: $created_at"
        },

        # ADS Templates
        "ads": {}
    }
}

class Localization:
    def __init__(self):
        self.data = MESSAGES
        self.lang = LANGUAGES
        self.errors = ERRORS

    def get(self, keys: str, lang_code: str = "ru") -> str:
        path = keys.split(".")

        data = self.data.get(lang_code)
        if not data:
            logger.warning(f"Not found language code: {lang_code}")
            return "[Incorrect language code]"

        for key in path:
            if not key:
                continue

            try: data = data[key]
            except (KeyError, TypeError): return self._missing_key(key)

        if isinstance(data, str):
            return data

        logger.warning(f"Key sequence incomplete: {path}")
        return f"[Key sequence incomplete: {path}]"

    def get_lang_selector_msg(self):
        data = self.lang.get("message")
        return data if data is not None else self._missing_key("message")
        
    def get_lang_selector_btn(self, key: str):
        data = self.lang.get(key)
        return data if data is not None else self._missing_key(key)

    def get_template(self, key: str, lang_code: str = "ru") -> Template:
        """
        :key: Name of template
        """
        data = self.get(f"templates.{key}", lang_code)
        return Template(data)

    def get_error_msg(self, error: Literal["reg", "web"], detail: Optional[str] = None) -> str:
        data = self.errors.get(error)
        if data is None:
            data = self._missing_key(error)

        if detail is None:
            return data
        
        return Template(data).safe_substitute(detail=detail)

    def _missing_key(self, key: str) -> str:
        logger.warning(f"Missing key: {key}")
        return f"[Missing key: {key}]"

localization = Localization()