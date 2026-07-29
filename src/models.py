from pydantic import BaseModel

from src.enums import Action, RouteScope, WaitStrategy


class ActionGO(BaseModel):
    method: Action = Action.GO
    general: RouteScope
    wait: WaitStrategy
