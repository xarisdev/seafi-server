from telegram import Update
from ..models.user import CreateUser

def get_user_model(update: Update) -> CreateUser:
    telegram_id: int = update.effective_sender.id
    username: str = update.effective_sender.name

    model = CreateUser(telegram_id=telegram_id, username=username)
    return model