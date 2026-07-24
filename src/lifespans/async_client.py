from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.api import app


@app.lifespan()
async def redis_lifespan(app: FastAPI):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport) as client:
        app.state.client = client
