import pytest
import redis.asyncio as asyncioredis
from fakeredis.aioredis import FakeRedis
from fastapi.testclient import TestClient

from src.api import app


@pytest.fixture(scope="function")
async def fakeredis():
    async with FakeRedis(decode_responses=True) as fredis:
        yield fredis


@pytest.fixture(scope="function")
async def mock_redis(monkeypatch):
    async with FakeRedis(decode_responses=True) as fakeredis:
        monkeypatch.setattr(asyncioredis, "from_url", lambda *args, **kwargs: fakeredis)
        yield fakeredis


@pytest.fixture(scope="function")
def client(mock_redis):
    with TestClient(app=app) as client:
        yield client
