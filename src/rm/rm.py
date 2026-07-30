import time

from fastapi import Request
from redis.asyncio import Redis

from src.core import ags_logger as logger
from src.core import config_settings, router_paths
from src.enums import Action, ReqLStrategy, RouteScope
from src.exceptions import UnknownIPErr
from src.models import ActionGO

from .limiter import sec_of_limit


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
        async with redis.pipeline(transaction=True) as pipe:
            pipe.zadd(key, {f"{request_time}": request_time})
            pipe.zremrangebyscore(key, "-inf", time.time() - rm)
            pipe.zcard(key)
            _, _, count_result = await pipe.execute()
        return count_result > count

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


async def router_path_status(redis, request: Request, path: str):
    lock_exc_key = f"exc:lock:{path}"
    current = router_paths[path]
    shaper = current.shaper_strategy or config_settings.server_shaper_strategy
    if shaper != ReqLStrategy.SHAPER and await limit_exceeded(request, path):
        return Action.BLOCK
    rrm = current.rrm if current.rrm is not None else config_settings.server_rrm
    rm = current.rm if current.rm is not None else config_settings.server_rm
    if rrm is None or (rm == rrm and shaper != ReqLStrategy.SHAPER):
        return Action.PROXY
    if (await redis.get(lock_exc_key)) is not None:
        return Action.ERROR

    if (
        current.max_wait_time is not None
        or config_settings.server_max_wait_time is not None
    ):
        count, rps = sec_of_limit(rrm)
        tact = rps / count
        current_max_wait_time = current.max_wait_time
        max_wait_time = (
            current_max_wait_time
            if current_max_wait_time is not None
            else config_settings.server_max_wait_time
        )
        if (
            max_wait_time
            and ((await redis.llen(f"queue:{path}")) * tact) > max_wait_time
        ):
            return Action.OVERLOADED
    route_wait = router_paths[path].wait
    return ActionGO(
        general=RouteScope.SPECIFIC,
        wait=(route_wait if route_wait is not None else config_settings.server_wait),
    )


async def all_path_status(redis: Redis, request: Request):
    lock_exc_key = "exc:lock:general"
    if (
        config_settings.server_shaper_strategy != ReqLStrategy.SHAPER
        and await limit_exceeded(request, "", all_path=True)
    ):
        return Action.BLOCK
    if not config_settings.server_rrm:
        return Action.PROXY
    if (await redis.get(lock_exc_key)) is not None:
        return Action.ERROR
    if config_settings.server_max_wait_time is not None:
        count, rps = sec_of_limit(config_settings.server_rrm)
        tact = rps / count
        if (
            (await redis.llen("queue:general")) * tact
        ) > config_settings.server_max_wait_time:
            return Action.OVERLOADED
    return ActionGO(
        general=RouteScope.GLOBAL,
        wait=config_settings.server_wait,
    )


async def evaluate(request: Request):
    path = request.url.path
    redis: Redis = request.app.state.redis
    while path != "":
        if path in router_paths:
            return await router_path_status(redis, request, path)
        path = (path.rsplit("/", maxsplit=1)[0] or "/") if path != "/" else ""
    if config_settings.all_path:
        return await all_path_status(redis, request)
    else:
        return Action.PROXY
