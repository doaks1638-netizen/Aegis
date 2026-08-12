from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

parent_path = Path(__file__).parent.parent


class Settings(BaseSettings):
    TG_TOKEN: str
    TG_CHAT_ID: str
    MQ_USER: str
    MQ_PASSWORD: str

    def get_mq_url(self):
        return f"amqp://{self.MQ_USER}:{self.MQ_PASSWORD}@mq:5672/"

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=parent_path / ".env",
        env_file_encoding="utf-8",
    )


settings = Settings() # type: ignore
