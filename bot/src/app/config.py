from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from pathlib import Path

CURRENT_FILE_DIR = Path(__file__).resolve().parent
ENV_PATH = CURRENT_FILE_DIR.parent.parent / ".env"

PERSISTENCE_FOLDER = CURRENT_FILE_DIR.parent.parent / "data"
PERSISTENCE_FOLDER.mkdir(exist_ok=True)
PERSISTENCE_PATH = PERSISTENCE_FOLDER / "persistence.pickle"

class Application(BaseSettings):
    APP_API_TOKEN: str
    TELEGRAM_BOT_TOKEN: str
    BASE_SERVER_URL: str
    WSS_SERVER_URL: str

    PERSISTENCE_PATH: str = str(PERSISTENCE_PATH)

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8"
    )

class Settings(
    Application
):
    pass

settings = Settings()