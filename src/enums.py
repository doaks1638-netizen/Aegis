from enum import StrEnum, auto


class ReqLStrategy(StrEnum):
    POLICER_LIMITER = auto()
    SHAPER = auto()


class WaitStrategy(StrEnum):
    FAST = auto()
    SLOW = auto()


class RouteScope(StrEnum):
    GLOBAL = auto()  # all_path
    SPECIFIC = auto()  # (/api/v1/...)


class Action(StrEnum):
    BLOCK = auto()
    GO = auto()
    PROXY = auto()
    ERROR = auto()
    OVERLOADED = auto()
