from telegram import (
    Update, Message, CallbackQuery, 
    ReplyKeyboardMarkup, ReplyKeyboardRemove, 
    InlineKeyboardMarkup, InlineKeyboardButton,
    )

from telegram.ext import (
    ApplicationBuilder, ContextTypes,
    CommandHandler, MessageHandler, CallbackQueryHandler,
    filters
)

from .config import settings
from ..scripts.web_agent import web_agent
from ..scripts.users import get_user_model

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
            url="/api/v1/users",
            method="POST",
            headers={"Authorization": settings.APP_API_TOKEN},
            json={"username": user.username, "telegram_id": user.telegram_id}
        )
        if result.data.get("status", "") != "success":
            await self.send_message(
                context,
                chat_id=user.telegram_id,
                text="Ошибка регистрации, попробуйте позднее"
                )
            return

        await self.delete_message(context, chat_id=user.telegram_id, message_id=update.effective_message.message_id)
        await self.send_message(context, chat_id=user.telegram_id, text="Добро пожаловать!") # Условный ответ

    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        #TODO logging
        user = get_user_model(update) # scripts

async def on_startup(application) -> None:
    await web_agent.init_client()

async def on_shutdown(application) -> None:
    await web_agent.close_client()

# bot
bot = TelegramBot()

# handlers
command_handler = CommandHandler("start", bot.start_command)

# app
app = (
    ApplicationBuilder()
    .token(settings.TELEGRAM_BOT_TOKEN)
    .post_init(on_startup)
    .post_shutdown(on_shutdown)
    .build()
)

app.add_handler(command_handler)