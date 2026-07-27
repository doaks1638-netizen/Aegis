import json

from fastapi import Request
from redis.asyncio import Redis


async def put_task(request: Request, path: str, general: bool, value: dict):
    redis: Redis = request.app.state.redis
    if not general: # TODO: сделать правльный и нормальный флаг
        key = "queue:general"
    else:
        key = f"queue:{path}"
    await redis.lpush(key, f"{json.dumps(value)}")
