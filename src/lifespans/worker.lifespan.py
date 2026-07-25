import asyncio

from fastapi import FastAPI

from src.api import app
from src.core import routes
from src.queue import worker_task


@app.lifespan()
async def redis_lifespan(app: FastAPI):
    for route in routes:
        asyncio.create_task(worker_task(route.path))
