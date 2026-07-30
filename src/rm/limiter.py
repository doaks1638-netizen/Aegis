from src.core import ags_logger as logger
from src.exceptions import RMTypeErr


def sec_of_limit(limit: str):
    match limit[-1]:
        case "s":
            rm = 1
        case "m":
            rm = 60
        case "h":
            rm = 3600
        case "d":
            rm = 216000
        case "y":
            rm = 12960000
        case _:
            logger.error("Such measurement units are not supported!!!")
            raise RMTypeErr(limit)
    return int(limit.split("/")[0]), int(rm)
