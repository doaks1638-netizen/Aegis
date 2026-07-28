import time

from fastapi import Request
from loguru import logger
from redis.asyncio import Redis

from src.core import config_settings, router_paths
from src.exceptions import RMTypeErr, UnknownIPErr

from .rm_enum import Action


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


async def limit_exceeded(request: Request, path: str, all_path: bool = False):
    request_time = time.time()
    redis: Redis = request.app.state.redis
    if config_settings.behind_nginx:
        client_ip = request.headers.get("x-real-ip", None)
    else:
        client_ip = request.client.host if request.client else None
    if not client_ip:
        logger.error(
            "Unknown IP type, please check that the service does not have NGINX in front of it."
        )
        raise UnknownIPErr(client_ip)

    async def checker(rm, key):
        if not rm:
            return False
        count, rm = sec_of_limit(rm)
        key = f"{key}:{client_ip}"
        await redis.zadd(key, {f"{request_time}": request_time})
        await redis.zremrangebyscore(key, "-inf", time.time() - rm)
        return await redis.zcard(key) > count

    if all_path:
        key = "limit:all_path"
        rm = config_settings.server_rm
        return await checker(rm, key)
    else:
        key = f"limit:{path}"
        rm = router_paths[path].rm
        if not rm:
            rm = config_settings.server_rm
        return await checker(rm, key)


async def evaluate(request: Request):
    path = request.url.path
    redis: Redis = request.app.state.redis
    while path != "":
        if path in router_paths:
            lock_exc_key = f"exc:lock:{path}"
            current = router_paths[path]
            shaper = current.shaper_strategy or config_settings.server_shaper_strategy
            if not shaper and await limit_exceeded(request, path):
                return Action.BLOCK
            rrm = current.rrm if current.rrm is not None else config_settings.server_rrm
            rm = current.rm if current.rm is not None else config_settings.server_rm
            if rrm is None or (
                rm == rrm and not shaper
            ):
                return Action.PROXY
            if (await redis.get(lock_exc_key)) is not None:
                return Action.ERROR

            if (
                current.max_wait_time is not None
                or config_settings.server_max_wait_time is not None
            ):
                count, rps = sec_of_limit(rrm)
                tact = rps / count
                is_overloaded = ((await redis.llen(f"queue:{path}")) * tact) > (  # pyright: ignore[reportOperatorIssue]
                    current.max_wait_time
                    if current.max_wait_time is not None
                    else config_settings.server_max_wait_time
                )
            else:
                is_overloaded = False
            return (
                Action.GO,
                True,
                router_paths[path].queue,
                is_overloaded,
            )  # True - matched path, take specific worker
        path = (path.rsplit("/", maxsplit=1)[0] or "/") if path != "/" else ""
    if config_settings.all_path:
        lock_exc_key = "exc:lock:general"
        if not config_settings.server_shaper_strategy and await limit_exceeded(
            request, "", all_path=True
        ):
            return Action.BLOCK
        if not config_settings.server_rrm:
            return Action.PROXY
        if (await redis.get(lock_exc_key)) is not None:
            return Action.ERROR
        if config_settings.server_max_wait_time is not None:
            count, rps = sec_of_limit(config_settings.server_rrm)
            tact = rps / count
            is_overloaded = (
                (await redis.llen("queue:general")) * tact
            ) > config_settings.server_max_wait_time
        else:
            is_overloaded = False
        return (
            Action.GO,
            False,
            config_settings.server_queue,
            is_overloaded,
        )  # False - take general worker
    else:
        return Action.PROXY
