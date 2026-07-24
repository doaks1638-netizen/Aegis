from ipaddress import ip_address
from typing import Annotated

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings

from .config_parser import config

RM = Annotated[str | None, Field(pattern=r"^\d+\/[smhdy]$", default=None)]


class Route(BaseModel):
    path: str
    rm: RM
    rrm: RM
    active: bool


class ConfigSettings(BaseSettings):
    # --- SETTINGS ---
    need_queue: bool
    responce_code: int = Field(default=202, gt=0, lt=600)

    # --- SERVER ---
    address: str

    @field_validator("address")
    @classmethod
    def address_checker(cls, value: str):
        ip_address(value.split(":")[0])
        return value

    server_rm: RM
    server_rrm: RM

    all_path: bool

    # --- ROUTES ---

    routes: list[Route] | list


config_settings = ConfigSettings(
    need_queue=config.get("settings", {}).get("queue", False),
    responce_code=config.get("settings", {}).get("code", 202),
    address=config["settings"]["address"],
    server_rm=config["settings"].get("rm", None),
    server_rrm=config["settings"].get("rrm", None),
    all_path=config["settings"].get("all_path", False),
    router=config.get("route"),
)
