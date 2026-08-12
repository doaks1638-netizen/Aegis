from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

parent_path: Path = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    REDIS_PASSWORD: str
    MQ_USER: str
    MQ_PASSWORD: str

    def get_mq_url(self) -> str:
        return f"amqp://{self.MQ_USER}:{self.MQ_PASSWORD}@mq:5672/"

    def get_redis_url(self) -> str:
        return f"redis://:{self.REDIS_PASSWORD}@redis:6379/0"

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=parent_path / ".env",
        env_file_encoding="utf-8",
    )


settings = Settings()  # pyright: ignore[reportCallIssue]
