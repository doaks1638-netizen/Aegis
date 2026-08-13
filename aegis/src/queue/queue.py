import json

from fastapi import Request
from redis.asyncio import Redis
from src.enums import RouteScope


async def put_task(request: Request, path: str, general: RouteScope, value: dict):
    redis: Redis = request.app.state.redis
    if general == RouteScope.GLOBAL:
        key = "queue:general"
    else:
        key = f"queue:{path}"
    await redis.lpush(key, f"{json.dumps(value)}")
