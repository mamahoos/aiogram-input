from __future__ import annotations

import pytest
from fakeredis import FakeAsyncRedis

from aiogram_input import InputStorage, RedisInputStorage, setup_input
from aiogram_input.types import WaitRecord
from aiogram import Dispatcher


@pytest.fixture
async def redis():
    client = FakeAsyncRedis(decode_responses=True)
    try:
        yield client
    finally:
        await client.aclose()


@pytest.fixture
def storage(redis) -> RedisInputStorage:
    return RedisInputStorage(redis, key_prefix="test:wait:")


@pytest.mark.asyncio
async def test_redis_storage_is_input_storage(storage: RedisInputStorage) -> None:
    assert isinstance(storage, InputStorage)


@pytest.mark.asyncio
async def test_redis_get_set_pop_roundtrip(storage: RedisInputStorage) -> None:
    record = WaitRecord(wait_id="w1", created_at=1.5)
    await storage.set(10, record)
    assert await storage.contains(10) is True
    assert await storage.get(10) == record
    assert await storage.pop(10) == record
    assert await storage.contains(10) is False
    assert await storage.get(10) is None


@pytest.mark.asyncio
async def test_redis_pop_if_is_wait_id_scoped(storage: RedisInputStorage) -> None:
    await storage.set(11, WaitRecord(wait_id="keep", created_at=2.0))
    assert await storage.pop_if(11, "other") is None
    assert await storage.contains(11) is True
    assert await storage.pop_if(11, "keep") == WaitRecord(wait_id="keep", created_at=2.0)
    assert await storage.contains(11) is False


@pytest.mark.asyncio
async def test_redis_ttl_rejected() -> None:
    with pytest.raises(ValueError, match="ttl"):
        RedisInputStorage(FakeAsyncRedis(), ttl=0)


@pytest.mark.asyncio
async def test_redis_ttl_sets_expiry(redis) -> None:
    storage = RedisInputStorage(redis, key_prefix="ttl:", ttl=60)
    await storage.set(1, WaitRecord(wait_id="t", created_at=1.0))
    ttl = await redis.ttl("ttl:1")
    assert 0 < ttl <= 60


@pytest.mark.asyncio
async def test_setup_input_accepts_redis_storage(redis) -> None:
    dp = Dispatcher()
    waiter = setup_input(dp, storage=RedisInputStorage(redis))
    assert waiter is not None


@pytest.mark.asyncio
async def test_redis_pop_missing_returns_none(storage: RedisInputStorage) -> None:
    assert await storage.pop(999) is None


@pytest.mark.asyncio
async def test_redis_loads_bytes_payload() -> None:
    record = WaitRecord(wait_id="b", created_at=3.0)
    raw = RedisInputStorage._dumps(record).encode()
    assert RedisInputStorage._loads(raw) == record


@pytest.mark.asyncio
async def test_redis_loads_invalid_payload_returns_none() -> None:
    assert RedisInputStorage._loads(b"nope") is None
    assert RedisInputStorage._loads('{"wait_id":""}') is None
