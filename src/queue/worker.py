import asyncio
import json
from uuid import uuid4

from fastapi import FastAPI
from redis import Redis

from src.api import proxy_pass_dict
from src.rm import sec_of_limit


async def worker_task(app: FastAPI, path: str, rrm: str):
    redis: Redis = app.state.redis
    count, rrm = sec_of_limit(rrm)
    tact = rrm / count
    key = f"queue:{path}" if path is not None else "queue:general"
    last_modifed_key = f"last_modifed:worker_{uuid4()}"
    while True:
        if await (last_modifed := redis.get(last_modifed_key)) <= tact:
            result = json.loads(await redis.brpop(key))
            response = await proxy_pass_dict(data=result["request"], app=app)
            if (lock_key := result["lock"]) is not None:
                await redis.lpush(lock_key, response)
            else:
                pass  # Скоро будет возможность вебхука, следите за релизами!
        else:
            await asyncio.sleep(rrm - last_modifed)
