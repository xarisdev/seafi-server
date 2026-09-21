import json

from telegram import (
    Update, Message, CallbackQuery,
    )

from telegram.ext import (
    ApplicationBuilder, PicklePersistence,
    ContextTypes,
    CommandHandler, MessageHandler, CallbackQueryHandler,
    filters
)

from .config import settings, PERSISTENCE_PATH

from ..web.seafi_api import seafi_api

from ..models.user import User
from ..web.models.users import UserSchema

from .localization import get_text, get_lang, get_web_error, get_reg_error
from .inline_keyboard import get_language_keyboard, get_menu_keyboard, get_back_menu

def get_user_model(update: Update, lang = None) -> User:
    model = User(
        telegram_id=update.effective_user.id,
        username=update.effective_user.username,
        language=lang
    )
    return model

class TelegramBotMessages():
    #TODO logging
    async def send_message(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int, **kwargs):
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                **kwargs
            )
        except Exception as e:
            print(e)
    async def edit_message(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int, **kwargs):
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                **kwargs
            )
        except Exception as e:
            print(e)
    async def delete_message(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int):
        try:
            result = await context.bot.delete_message(
                chat_id=chat_id,
                message_id=message_id
            )
            return result
        except Exception as e:
            print(e)

class TelegramBotTextHandler():
    async def text_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = get_user_model(update)
        print(f"{user.username} [{user.telegram_id}]: {update.message.text}")

class TelegramBot(TelegramBotMessages, TelegramBotTextHandler):
    def __init__(self):
        super().__init__()

    def _user_lang(self, context: ContextTypes.DEFAULT_TYPE) -> str:
        return context.user_data.get("lang", "ru")

    def _user_authenticator(self, context: ContextTypes.DEFAULT_TYPE) -> bool:
        return context.user_data.get("is_auth", False)

    async def get_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE, reg=False):
        is_auth = self._user_authenticator(context)
        if not is_auth and reg == False:
            await self.send_message(context,
                              chat_id=update.effective_user.id,
                              text=get_reg_error())
            return is_auth

        user = get_user_model(update, self._user_lang(context))
        return user

    async def web_error(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int, detail):
        await self.send_message(context,
                                chat_id=chat_id,
                                text=get_web_error().replace("--detail", str(detail)))

    # --- callback ---

    async def callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        user = await self.get_user(update, context)
        if not user:
            print("404")

        try:
            callback_data = json.loads(query.data)
            action = callback_data.get("data")

            match action:
                # --- language ---
                case "lang_ru":
                    await self.select_language(update, context, lang=action)

                case "lang_kg": pass
                case "lang_en": pass

                case "sub_info":
                    await self.sub_query(update, context, user)

                case "set_filter":
                    pass

                case "view_prof":
                    await self.profile_query(update, context, user)

                case "set_menu":
                    await self.menu_query(update, context, user)

                case _:
                    pass

        except Exception as exc:
            print(exc)

    # --- query ---

    async def profile_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user: User):
        result = await seafi_api.get_user(user.telegram_id)

        if isinstance(result, UserSchema):
            text = (
                "Профиль\n"
                f"ID: {result.telegram_id}\n"
                f"Username: {result.username}\n"
                f"Создан: {result.created_at.date().isoformat()}\n"
            )
            await self.edit_message(
                context,
                chat_id=user.telegram_id,
                message_id=update.callback_query.message.message_id,
                text=text,
                reply_markup=get_back_menu()
            )

    async def sub_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user: User):
        pass

    async def menu_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user: User):
        await self.edit_message(context,
                                chat_id=user.telegram_id,
                                message_id=update.callback_query.message.message_id,
                                text="Меню:",
                                reply_markup=get_menu_keyboard())

    # --- /commands ---
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = await self.get_user(update, context, reg=True)
        if not user: return

        text = ""
        reply_markup = None

        model = await seafi_api.create_user(telegram_id=user.telegram_id, username=user.username)
        if isinstance(model, UserSchema):
            context.user_data["is_auth"] = True
            text = get_lang("message")
            reply_markup = get_language_keyboard()
        else:
            if model == 409:
                db_model = await seafi_api.get_user(user.telegram_id)
                if isinstance(db_model, UserSchema):
                    user.language = db_model.language
                    context.user_data["lang"] = user.language
                    context.user_data["is_auth"] = True

                    if not user.language:
                        text = get_lang("message")
                        reply_markup = get_language_keyboard()
                    else:
                        text = get_text("menu", lang=user.language)
                        reply_markup = get_menu_keyboard(user.language)
                else:
                    await self.web_error(context, user.telegram_id, detail=db_model)
                    return
            else:
                await self.web_error(context, user.telegram_id, detail=model)
                return

        await self.send_message(context=context,
                                chat_id=user.telegram_id,
                                text=text,
                                reply_markup=reply_markup)

    # --- scripts ---

    async def select_language(self, update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str):
        language_code = lang.split('_')[1]
        telegram_id = update.effective_user.id

        result = await seafi_api.patch_user(telegram_id=telegram_id, language=language_code)
        if result != 202:
            await self.web_error(context, telegram_id, detail=result)
            return

        context.user_data["lang"] = language_code
        await self.send_message(context,
                                chat_id=telegram_id,
                                text=get_text('menu', lang=language_code),
                                reply_markup=get_menu_keyboard(language_code))

async def on_startup(application) -> None:
    await seafi_api.init_client()
async def on_shutdown(application) -> None:
    await seafi_api.close_client()

# bot
bot = TelegramBot()

persistence = PicklePersistence(PERSISTENCE_PATH)

# handlers
start_command_handler = CommandHandler("start", bot.start_command)
callback_handler = CallbackQueryHandler(bot.callback_handler)

# app
app = (
    ApplicationBuilder()
    .token(settings.TELEGRAM_BOT_TOKEN)
    .persistence(persistence)
    .post_init(on_startup)
    .post_shutdown(on_shutdown)
    .build()
)

app.add_handler(start_command_handler)
app.add_handler(callback_handler)