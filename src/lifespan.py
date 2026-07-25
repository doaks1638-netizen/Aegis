import asyncio

import redis.asyncio as asyncioredis
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.api import app
from src.core import config_settings, routes, settings
from src.queue import worker_task


@app.lifespan()
async def lifespan(app: FastAPI):
    transport = ASGITransport(app=app)
    async with (
        AsyncClient(transport=transport) as client,
        asyncioredis.from_url(settings.get_redis_url(), decode_responses=True) as redis,
    ):
        app.state.client = client
        app.state.redis = redis
        for route in routes:
            asyncio.create_task(worker_task(app, route.path, route.rrm))
        if (
            config_settings.all_path
            and config_settings.server_rm
            and config_settings.server_rrm
        ):
            asyncio.create_task(worker_task(app, None, config_settings.server_rrm))
        yield
