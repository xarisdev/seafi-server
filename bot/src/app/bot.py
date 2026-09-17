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

from ..models.web import ServerUser

from .inline_keyboard import get_menu_keyboard, get_back_menu

class TelegramBotMessage():
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

class TelegramBot(TelegramBotMessage):
    def __init__(self):
        super().__init__()

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        #TODO logging
        user = get_user_model(update)
        result = await web_agent.fetch(
            url="/api/v1/user",
            method="POST",
            headers={"Authorization": settings.APP_API_TOKEN},
            json={"username": user.username, "telegram_id": user.telegram_id}
        )
        if result.status_code not in [201, 409]:
            await self.send_message(
                context,
                chat_id=user.telegram_id,
                text="Ошибка регистрации, попробуйте позднее"
                )
            return

        await self.send_message(
            context,
            chat_id=user.telegram_id,
            text="Добро пожаловать! Меню:",
            reply_markup=get_menu_keyboard(False)
        )

    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        #TODO logging
        user = get_user_model(update) # scripts

    async def callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        try:
            callback_data = json.loads(query.data)
            action = callback_data.get("a")

            if action == "view_prof":
                await self.profile_command(update, context)
            elif action == "set_parser":
                pass
            elif action == "set_menu":
                await self.menu_command(update, context)

        except Exception as exc:
            print(exc)

    async def profile_command(self, update: Update, context):
        user = get_user_model(update)
        result = await web_agent.fetch(
            url=f"/api/v1/user/{user.telegram_id}",
            headers={"Authorization": settings.APP_API_TOKEN}
        )
        if result.status_code != 200:
            return

        server_user = ServerUser(**result.data)
        text = (
            "Профиль\n"
            f"ID: {server_user.telegram_id}\n"
            f"Username: {server_user.username}\n"
            f"Регистрация: {server_user.created_at.split("T")[0]}"
        )
        await self.edit_message(
            context,
            chat_id=user.telegram_id,
            message_id=update.callback_query.message.message_id,
            text=text,
            reply_markup=get_back_menu()
        )

    async def menu_command(self, update: Update, context):
        user = get_user_model(update)
        await self.edit_message(
            context,
            chat_id=user.telegram_id,
            message_id=update.callback_query.message.message_id,
            text="Меню:",
            reply_markup=get_menu_keyboard(False)
        )


async def on_startup(application) -> None:
    await web_agent.init_client()

async def on_shutdown(application) -> None:
    await web_agent.close_client()

# bot
bot = TelegramBot()

# handlers
command_handler = CommandHandler("start", bot.start_command)
callback_handler = CallbackQueryHandler(bot.callback_handler)

# app
app = (
    ApplicationBuilder()
    .token(settings.TELEGRAM_BOT_TOKEN)
    .post_init(on_startup)
    .post_shutdown(on_shutdown)
    .build()
)

app.add_handler(command_handler)
app.add_handler(callback_handler)