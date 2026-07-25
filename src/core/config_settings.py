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
    active: bool = True
    queue: bool = False


class ConfigSettings(BaseSettings):
    # --- SETTINGS ---
    need_queue: bool
    response_code: int = Field(default=202, gt=0, lt=600)

    # --- SERVER ---
    address: str

    @field_validator("address")
    @classmethod
    def address_checker(cls, value: str):
        ip_address(value.split(":")[0])
        return value

    server_rm: RM
    server_rrm: RM
    server_queue: bool

    all_path: bool


config_settings = ConfigSettings(
    need_queue=config.get("settings", {}).get("queue", False),
    responce_code=config.get("settings", {}).get("code", 202),
    address=config["settings"]["address"],
    server_rm=config["settings"].get("rm", None),
    server_rrm=config["settings"].get("rrm", None),
    queue=config["settings"].get("rrm", False),
    all_path=config["settings"].get("all_path", False),
)
routes = [Route.model_validate(route) for route in config.get("route")]
router_paths = {router.path: router for router in routes}
