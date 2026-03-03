from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    # Database
    DATABASE_URL: str = (
        "postgresql+asyncpg://tax_shield:taxshield_dev_2024@localhost:5432/tax_shield"
    )

    # Auth
    JWT_SECRET_KEY: str = "change-me-to-a-random-64-char-string"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Encryption
    FIELD_ENCRYPTION_KEY: str = "change-me-to-a-32-byte-base64-key"

    # Anthropic
    ANTHROPIC_API_KEY: str = ""

    # Plaid
    PLAID_CLIENT_ID: str = ""
    PLAID_SECRET: str = ""
    PLAID_ENV: str = "sandbox"

    # App
    APP_ENV: str = "development"
    CORS_ORIGINS: str = "http://127.0.0.1:8000,http://localhost:8000"
    ADMIN_EMAIL: str = "admin@taxshield.local"
    ADMIN_PASSWORD: str = "change-me"


settings = Settings()
