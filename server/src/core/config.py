from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from pathlib import Path

CURRENT_FILE_DIR = Path(__file__).resolve().parent
ENV_PATH = CURRENT_FILE_DIR.parent.parent / ".env"

class Application(BaseSettings):
    APP_NAME: str
    APP_TOKEN: str
    ADMIN_ID: str

    LOCALHOST: str

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8"
    )

class DataBase(BaseSettings):
    DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8"
    )

class PaymentService(BaseSettings):
    LAVA_API_URL: str
    LAVA_API_KEY: str
    LAVA_API_PASSWORD: str

    REDIRECT_URL: str
    REDIRECT_URI: str

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8"
    )

class TestSettings(BaseSettings):
    TEST_TELEGRAM_ID: int
    TEST_USERNAME: str

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        enable_decoding="utf-8"
    )

class Settings(
    Application,
    DataBase,
    PaymentService,
    TestSettings
): pass

settings = Settings()