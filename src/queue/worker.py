import asyncio
import json
import time
from uuid import uuid4

from fastapi import FastAPI
from loguru import logger
from redis import Redis

from src.api import proxy_pass_dict
from src.rm import sec_of_limit


async def worker_task(app: FastAPI, path: str, rrm: str):
    redis: Redis = app.state.redis
    count, rrm = sec_of_limit(rrm)
    tact = rrm / count
    key = f"queue:{path}" if path is not None else "queue:general"
    last_modifed_key = f"last_modifed:worker_{uuid4()}"
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
                    else tact + 10
                )
            ) > tact:
                logger.info("Great! We can get the value for the request.")
                result = await redis.brpop(key, timeout=4.9)
                if result is None:
                    continue
                result = json.loads(result[1])
                logger.info("Received a request, proxying it.")
                response = await proxy_pass_dict(data=result["request"], app=app)
                if (lock_key := result["lock"]) is not None:
                    logger.info("The query result needs to responce to client")
                    await redis.lpush(lock_key, json.dumps(response))
                    await redis.set(last_modifed_key, time.time())
                logger.info("The query result do not needs to responce to client")
            else:
                logger.info("To try the next request, wait.")
                await asyncio.sleep(tact - last_modifed)
        except Exception as e:  # noqa: BLE001
            logger.error(f"Worker exc - {e}!!!")
            await asyncio.sleep(1)
