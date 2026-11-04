from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from pathlib import Path

CURRENT_FILE_DIR = Path(__file__).resolve().parent
ENV_PATH = CURRENT_FILE_DIR.parent.parent / ".env"

class Application(BaseSettings):
    APP_NAME: str = "seafi-server"
    APP_ENV: str = "development"
    X_API_KEY: str = "test-api-key"
    X_WSS_KEY: str = "test-wss-key"
    ADMIN_KEY: str = "test-admin-key"
    ADMIN_TELEGRAM_ID: int | None = None

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8"
    )

class PostgresDataBase(BaseSettings):
    POSTGRES_DB: str = "seafi"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/seafi"

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8"
    )

class PaymentService(BaseSettings):
    LAVA_API_URL: str = "https://gate.lava.top/api"
    LAVA_WEBHOOK_SECRET: str = "test-lava-webhook-secret"
    LAVA_X_API_KEY: str = "test-lava-x-api-key"

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8"
    )

class TestSettings(BaseSettings):
    TEST_TELEGRAM_ID: int = 123456789
    TEST_USERNAME: str = "test-user"

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8"
    )

class Settings(
    Application,
    PostgresDataBase,
    PaymentService,
    TestSettings
): pass

settings = Settings()