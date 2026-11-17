from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Automated Multi-Platform Posting System"
    APP_VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 4000

    # Dry-run flag for offline testing and mock execution
    DRY_RUN_MODE: bool = True

    # Telegram Credentials
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None

    # Discord Credentials
    DISCORD_WEBHOOK_URL: Optional[str] = None

    # Slack Credentials
    SLACK_WEBHOOK_URL: Optional[str] = None

    # Mastodon Credentials
    MASTODON_INSTANCE_URL: str = "https://mastodon.social"
    MASTODON_ACCESS_TOKEN: Optional[str] = None

    # Dev.to Credentials
    DEVTO_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
