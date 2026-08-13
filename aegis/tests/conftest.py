from unittest.mock import AsyncMock

import aio_pika as apika
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
    fakeredis = FakeRedis(decode_responses=True)
    monkeypatch.setattr(asyncioredis, "from_url", lambda *args, **kwargs: fakeredis)
    yield fakeredis


@pytest.fixture(scope="function", autouse=True)
async def mock_mq(monkeypatch):
    fake_connection = AsyncMock()
    fake_connection.channel.return_value = AsyncMock()

    async def _get_fake_connection(*args, **kwargs):
        return fake_connection

    monkeypatch.setattr(apika, "connect_robust", _get_fake_connection)
    yield fakeredis


@pytest.fixture(scope="function")
def client(mock_redis):
    with TestClient(app=app) as client:
        yield client
