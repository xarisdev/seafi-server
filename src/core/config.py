from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from pathlib import Path

CURRENT_FILE_DIR = Path(__file__).resolve().parent
ENV_PATH = CURRENT_FILE_DIR.parent.parent / ".env"

class Application(BaseSettings):
    APP_NAME: str = "seafi-server"
    X_API_KEY: str
    X_WSS_KEY: str
    ADMIN_KEY: str

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8"
    )

class PostgresDataBase(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_URL: str

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8"
    )

class PaymentService(BaseSettings):
    LAVA_API_URL: str = "https://gate.lava.top/api"
    LAVA_WEBHOOK_SECRET: str
    LAVA_X_API_KEY: str

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
    PostgresDataBase,
    PaymentService,
    TestSettings
): pass

settings = Settings()