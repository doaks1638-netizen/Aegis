from enum import Enum


class Action(str, Enum):
    BLOCK = "BLOCK"
    GO = "GO"
    PROXY = "PROXY"
    ERROR = 'ERROR'
