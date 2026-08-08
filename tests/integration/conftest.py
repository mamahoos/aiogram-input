from __future__ import annotations

import os
import uuid

import pytest
from redis.asyncio import Redis

from aiogram_input import RedisInputStorage


@pytest.fixture
def redis_url() -> str:
    return os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/15")


@pytest.fixture
async def redis(redis_url: str):
    client = Redis.from_url(redis_url, decode_responses=True)
    await client.ping()
    prefix = f"aiogram_input:it:{uuid.uuid4().hex}:"
    try:
        yield client, prefix
    finally:
        keys = [key async for key in client.scan_iter(match=f"{prefix}*")]
        if keys:
            await client.delete(*keys)
        await client.aclose()


@pytest.fixture
async def storage(redis) -> RedisInputStorage:
    client, prefix = redis
    return RedisInputStorage(client, key_prefix=prefix)
