import asyncio
import json
import time
from uuid import uuid4

from fastapi import FastAPI
from loguru import logger
from redis.asyncio import Redis

from src.api import proxy_pass_dict
from src.core import config_settings, router_paths
from src.rm import sec_of_limit


async def worker_task(app: FastAPI, path: str | None, rrm: str):
    # Each worker works with one queue, race-condition is not possible
    redis: Redis = app.state.redis
    count, rps = sec_of_limit(rrm)
    tact = rps / count
    path = path if path is not None else "general"
    key = f"queue:{path}"
    last_modifed_key = f"last_modifed:worker_{path}"  # last-changed key for each worker
    exc_key = f"exc:{path}"
    lock_exc_key = f"exc:lock:{path}"
    logger.info("The worker has initialized.")
    while True:
        try:
            logger.info(
                "We look at how much time has passed since the last request to avoid violating the RPS"
            )
            last_modifed_key_value = await redis.get(last_modifed_key)
            if (
                last_modifed := time.time()
                - float(
                    last_modifed_key_value
                    if last_modifed_key_value is not None
                    else tact + 1
                )
            ) > tact:
                logger.info("Great! We can get the value for the request.")
                result = await redis.brpop(key, timeout=4.9)
                if result is None:
                    continue
                result = json.loads(result[1])
                logger.info("Received a request, proxying it.")
                response, exc_flag = await proxy_pass_dict(
                    data=result["request"], app=app
                )
                if exc_flag:
                    if path == "general":
                        sec_cooldown = config_settings.server_sec_cooldown
                        max_failures = config_settings.server_max_failures
                    elif (
                        path_sec_cooldown := router_paths[path].sec_cooldown
                    ) is not None and (
                        path_max_failures := router_paths[path].max_failures
                    ) is not None:
                        sec_cooldown = path_sec_cooldown
                        max_failures = path_max_failures
                    elif (
                        path_max_failures := router_paths[path].max_failures
                    ) is not None:
                        sec_cooldown = config_settings.server_sec_cooldown
                        max_failures = path_max_failures
                    else:
                        max_failures = None
                        sec_cooldown = 0
                    if max_failures is not None:
                        fails = await redis.incr(exc_key)
                        if fails >= max_failures:
                            await redis.set(lock_exc_key, "1", ex=int(sec_cooldown))
                            await redis.delete(exc_key)
                else:
                    await redis.delete(exc_key)
                if (lock_key := result["lock"]) is not None:
                    logger.info("The query result needs to responce to client")
                    await redis.lpush(lock_key, json.dumps(response))
                    await redis.expire(lock_key, 10)
                await redis.set(
                    last_modifed_key, time.time(), ex=max(60, int(tact * 2))
                )
                logger.info("The query result do not needs to responce to client")
            else:
                logger.info("To try the next request, wait.")
                await asyncio.sleep(tact - last_modifed)
        except Exception as e:  # noqa: BLE001
            logger.error(f"Worker exc - {e}!!!")
            await asyncio.sleep(1)
