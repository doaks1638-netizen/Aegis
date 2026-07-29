from pydantic import BaseModel

from src.rm import Action


class ActionGO(BaseModel):
    method: Action = Action.GO
    general: bool
    wait_need: bool
    is_overloaded: bool
