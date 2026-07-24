import redis.asyncio as asyncioredis
from fastapi import FastAPI

from src.api import app
from src.core import settings


@app.lifespan()
async def redis_lifespan(app: FastAPI):
    async with asyncioredis.from_url(
        settings.get_redis_url(), decode_responses=True
    ) as redis:
        app.state.redis = redis
