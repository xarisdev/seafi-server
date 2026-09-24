import json
import logging

from telegram import Update, Message

from telegram.ext import (
    ApplicationBuilder, PicklePersistence,
    ContextTypes,
    CommandHandler, CallbackQueryHandler
)

from .config import settings

from .localization import localization
from .inline_keyboard import get_menu_keyboard, get_language_keyboard, get_back_menu

from ..web.seafi_api import seafi_api
from ..models.user import UserRead, UserInternal

logger = logging.getLogger("telegram.bot")

# ------------ Bot MessageSenderMixin  ------------

class MessageSenderMixin:
    async def send_message(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int, **kwargs):
        try:
            message: Message = await context.bot.send_message(
                chat_id=chat_id,
                **kwargs
            )
            logger.info(f"Send message [{message.message_id}] to chat: {chat_id}")
        except Exception:
            logger.error(f"Failed to send message to chat: {chat_id}", exc_info=True)

    async def edit_message(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int, **kwargs):
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                **kwargs
            )
            logger.info(f"Edit message [{message_id}] in chat: {chat_id}")
        except Exception:
            logger.error(f"Failed to edit message [{message_id}] in chat: {chat_id}", exc_info=True)

    async def delete_message(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int):
        try:
            await context.bot.delete_message(
                chat_id=chat_id,
                message_id=message_id
            )
            logger.info(f"Delete message [{message_id}] in chat: {chat_id}")
        except Exception:
            logger.error(f"Failed to delete message [{message_id}] in chat: {chat_id}", exc_info=True)

# ------------ User scripts ------------

def get_user_auth(context: ContextTypes.DEFAULT_TYPE) -> bool:
    return context.user_data.get("is_auth", False)

def set_user_unauth(context: ContextTypes.DEFAULT_TYPE):
    context.user_data["is_auth"] = False

# ------------ Main class ------------

class TelegramBot(MessageSenderMixin):

    # ------------ Scripts ------------

    async def get_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE, reg=False):
        is_auth = get_user_auth(context)

        if not is_auth and not reg:
            await self.send_message(
                context,
                chat_id=update.effective_user.id,
                text=localization.get_error_msg("reg")
            )
            return

        lang = context.user_data.get("language") or "ru"
        user = UserInternal(
            telegram_id=update.effective_user.id,
            username=update.effective_user.username,
            language=lang
        )
        return user

    async def web_error(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int, detail):
        logger.warning(f"Web error initialized. chat_id: {chat_id}, detail: {detail}")
        await self.send_message(
            context,
            chat_id=chat_id,
            text=localization.get_error_msg("web", detail)
        )

    # ------------ Callback query handler ------------

    async def callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        user = await self.get_user(update, context)
        if user is None: return

        try:
            callback_data = json.loads(query.data)
            action: str = callback_data.get("data")

            # ------------ Language selector buttons ------------

            if "lang_" in action:
                lang_code = action.split("_")[1]
                await self.select_language_query(
                    update=update,
                    context=context,
                    user=user,
                    lang_code=lang_code
                )

            # ------------ Menu buttons ------------

            elif action == "sub_info":
                await self.sub_query(
                    update=update,
                    context=context,
                    user=user
                )

            elif action == "set_filter":
                pass

            elif action == "view_prof":
                await self.profile_query(update, context, user)

            elif action == "set_menu":
                await self.menu_query(update, context, user)

            # ------------ Subscription control buttons ------------

            elif action == "": # placeholder
                pass

            # ------------ Unexpected query ------------

            else:
                logger.warning(f"Unexpected callback action. {action!r}, chat: {user.telegram_id}")

        except Exception:
            logger.error("Unexpected exception. [callback_handler]", exc_info=True)

    # ------------ Query scripts ------------

    async def select_language_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user: UserInternal, lang_code: str):
        result = await seafi_api.patch_user(telegram_id=user.telegram_id, language=lang_code)
        if result != 202:
            await self.web_error(context, user.telegram_id, detail=result)
            return

        context.user_data["language"] = lang_code
        await self.send_message(context,
                                chat_id=user.telegram_id,
                                text=localization.get("menu", lang_code=lang_code),
                                reply_markup=get_menu_keyboard(lang_code))

    async def profile_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user: UserInternal):
        db_user: UserRead = await seafi_api.get_user(user.telegram_id)

        if isinstance(db_user, UserRead):
            text = localization.get_template("profile", lang_code=db_user.language)
            text = text.substitute(
                id=db_user.telegram_id,
                username=db_user.username,
                created_at=db_user.created_at.date().isoformat()
            )
            reply_markup = get_back_menu(db_user.language)
        else:
            set_user_unauth(context)
            text = localization.get_error_msg("reg")
            reply_markup = None

        await self.edit_message(
            context,
            chat_id=user.telegram_id,
            message_id=update.callback_query.message.message_id,
            text=text,
            reply_markup=reply_markup
        )

    async def sub_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user: UserInternal):
        pass

    async def menu_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user: UserInternal):
        await self.edit_message(context,
                                chat_id=user.telegram_id,
                                message_id=update.callback_query.message.message_id,
                                text=localization.get("menu", lang_code=user.language),
                                reply_markup=get_menu_keyboard(user.language))

    # --- Command handlers ---
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = await self.get_user(update, context, reg=True)
        if user is None:
            return

        text = ""
        reply_markup = None

        db_user = await seafi_api.create_user(telegram_id=user.telegram_id, username=user.username)

        if isinstance(db_user, UserRead):
            context.user_data["is_auth"] = True
            text = localization.get_lang_selector_msg()
            reply_markup = get_language_keyboard()

        elif db_user == 409:
            db_user = await seafi_api.get_user(user.telegram_id)

            if isinstance(db_user, UserRead):
                context.user_data["is_auth"] = True
                context.user_data["language"] = db_user.language

                text = localization.get("menu", lang_code=db_user.language)
                reply_markup = get_menu_keyboard(db_user.language)

            else:
                await self.web_error(context, user.telegram_id, detail=db_user)
                return

        else:
            await self.web_error(context, user.telegram_id, detail=db_user)
            return

        await self.send_message(context=context,
                                chat_id=user.telegram_id,
                                text=text,
                                reply_markup=reply_markup)

async def on_startup(application) -> None:
    await seafi_api.init_client()
    logger.info("Application started")

async def on_shutdown(application) -> None:
    await seafi_api.close_client()
    logger.info("Application stopped")

# bot
bot = TelegramBot()

persistence = PicklePersistence(settings.PERSISTENCE_PATH)

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