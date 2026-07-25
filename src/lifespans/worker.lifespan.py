import asyncio

from fastapi import FastAPI

from src.api import app
from src.core import routes, config_settings
from src.queue import worker_task


@app.lifespan()
async def redis_lifespan(app: FastAPI):
    for route in routes:
        asyncio.create_task(worker_task(app, route.path, route.rrm))
    if (
        config_settings.all_path
        and config_settings.server_rm
        and config_settings.server_rrm
    ):
        asyncio.create_task(worker_task(app, None, route.rrm))
