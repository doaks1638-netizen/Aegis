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
    wait_need: bool = False
    max_wait_time: float | None = None
    max_failures: int | None
    sec_cooldown: float | None
    shaper_strategy: bool = False


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
    server_wait_need: bool

    all_path: bool
    behind_nginx: bool
    server_max_wait_time: float | None
    server_max_failures: int | None
    server_sec_cooldown: float
    server_shaper_strategy: bool


config_settings = ConfigSettings(
    need_queue=config.get("settings", {}).get("queue", False),
    response_code=config.get("settings", {}).get("code", 202),
    address=config["settings"]["address"],
    server_rm=config["settings"].get("rm", None),
    server_rrm=config["settings"].get("rrm", None),
    server_wait_need=config["settings"].get("wait_need", False),
    all_path=config["settings"].get("all_path", False),
    behind_nginx=config["settings"].get("behind_nginx", False),
    server_max_wait_time=config["settings"].get("max_wait_time", None),
    server_max_failures=config["settings"].get("max_failures", None),
    server_sec_cooldown=config["settings"].get("sec_cooldown", 5),
    server_shaper_strategy=config["settings"].get("shaper_strategy", False),
)
routes = [Route.model_validate(route) for route in config.get("route", [])]
router_paths = {router.path: router for router in routes}
