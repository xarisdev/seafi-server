import json

from telegram import (
    Update, Message, CallbackQuery,
    )

from telegram.ext import (
    ApplicationBuilder, ContextTypes,
    CommandHandler, MessageHandler, CallbackQueryHandler,
    filters
)

from .config import settings

from ..scripts.web_agent import web_agent
from ..scripts.users import get_user_model

from ..models.web import UserSchema

from .localization import get_text
from .inline_keyboard import get_menu_keyboard, get_back_menu

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

class TelegramBotWeb():
    async def registration_user(self, user: UserSchema):
        response = await web_agent.fetch(
            url="/api/v1/users",
            method="POST",
            headers={"X-Api-Key": settings.APP_API_TOKEN},
            json={"username": user.username, "telegram_id": user.telegram_id}
        )
        return response
    
    async def get_server_user_profile(self, telegram_id) -> UserSchema | int:
        response = await web_agent.fetch(
            url=f"/api/v1/users/{telegram_id}",
            headers={"X-Api-Key": settings.APP_API_TOKEN}
        )
        if response.status_code == 200:
            model = UserSchema(**response.data)
            return model
        
        return response.status_code

    async def get_subs_info(self, telegram_id: int):
        response = await web_agent.fetch(
            url=f"/api/v1/payments/products?telegram_id={telegram_id}",
            headers={"X-Api-Key": settings.APP_API_TOKEN}
        )
        ...

class TelegramBot(TelegramBotWeb, TelegramBotMessages, TelegramBotTextHandler):
    def __init__(self):
        super().__init__()

    # --- callback ---

    async def callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        try:
            callback_data = json.loads(query.data)
            action = callback_data.get("data")

            match action:
                case "sub_info":
                    await self.sub_query(update, context)

                case "set_filter":
                    pass

                case "view_prof":
                    await self.profile_query(update, context)

                case "set_menu":
                    await self.menu_query(update, context)

                case _:
                    pass

        except Exception as exc:
            print(exc)

    # --- query ---

    async def profile_query(self, update: Update, context):
        user = get_user_model(update)
        result = await self.get_server_user_profile(user.telegram_id)
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

    async def sub_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        pass

    async def menu_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = get_user_model(update)
        result = await self.get_server_user_profile(user.telegram_id)
        if result == 404:
            await self.send_message(context,
                                    chat_id=user.telegram_id,
                                    text="Вы не зарегистрированы! - /start")
            return
        await self.edit_message(context,
                                chat_id=user.telegram_id,
                                message_id=update.callback_query.message.message_id,
                                text="Меню:",
                                reply_markup=get_menu_keyboard())

    # --- /commands ---
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = get_user_model(update)

        response = await self.registration_user(user)
        if response.status_code in [201, 409]:
            await self.send_message(context,
                                    chat_id=user.telegram_id,
                                    text="Добро пожаловать! Меню:",
                                    reply_markup=get_menu_keyboard())
        else:
            await self.send_message(context,
                                    chat_id=user.telegram_id,
                                    text="Ошибка регистрации, попробуйте позднее.")

    async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = get_user_model(update)

        await self.send_message(context,
                                chat_id=user.telegram_id,
                                text="Меню:",
                                reply_markup=get_menu_keyboard())


async def on_startup(application) -> None:
    await web_agent.init_client()
async def on_shutdown(application) -> None:
    await web_agent.close_client()

# bot
bot = TelegramBot()

# handlers
start_command_handler = CommandHandler("start", bot.start_command)
menu_command_handler = CommandHandler("menu", bot.menu_command)
callback_handler = CallbackQueryHandler(bot.callback_handler)

# app
app = (
    ApplicationBuilder()
    .token(settings.TELEGRAM_BOT_TOKEN)
    .post_init(on_startup)
    .post_shutdown(on_shutdown)
    .build()
)

app.add_handler(start_command_handler)
app.add_handler(menu_command_handler)
app.add_handler(callback_handler)