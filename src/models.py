from pydantic import BaseModel

from src.rm import Action


class ActionGO(BaseModel):
    method: Action = Action.GO
    general: bool
    is_queue: bool
    is_overloaded: bool
