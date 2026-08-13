import asyncio
from contextlib import asynccontextmanager

import aio_pika as apika
import redis.asyncio as asyncioredis
from fastapi import FastAPI
from httpx import AsyncClient
from src.core import config_settings, routes, settings
from src.queue import worker_task


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with (
        AsyncClient() as client,
        asyncioredis.from_url(
            settings.get_redis_url(), decode_responses=True, socket_timeout=None
        ) as redis,
        await apika.connect_robust(url=settings.get_mq_url()) as mq,
    ):
        app.state.client = client
        app.state.redis = redis
        app.state.mq = mq
        tasks: list[asyncio.Task] = []
        for route in routes:
            if isinstance(route.rrm, str):
                tasks.append(
                    asyncio.create_task(worker_task(app, route.path, route.rrm))
                )
        if (
            config_settings.all_path
            and config_settings.server_rm
            and config_settings.server_rrm
        ):
            tasks.append(
                asyncio.create_task(worker_task(app, None, config_settings.server_rrm))
            )
        yield
        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)
