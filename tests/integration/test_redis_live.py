from __future__ import annotations

import asyncio

import pytest
from aiogram import Dispatcher
from redis.asyncio import Redis

from aiogram_input import InputWaiter, RedisInputStorage, setup_input
from aiogram_input.registry import WaitRegistry
from aiogram_input.session import SessionManager
from aiogram_input.types import WaitRecord
from tests.helpers import make_message

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_live_redis_roundtrip(storage: RedisInputStorage) -> None:
    record = WaitRecord(wait_id="live-1", created_at=10.0)
    await storage.set(1001, record)
    assert await storage.contains(1001) is True
    assert await storage.get(1001) == record
    assert await storage.pop(1001) == record
    assert await storage.contains(1001) is False


@pytest.mark.asyncio
async def test_live_redis_pop_if_atomic(storage: RedisInputStorage) -> None:
    await storage.set(1002, WaitRecord(wait_id="keep", created_at=11.0))
    assert await storage.pop_if(1002, "nope") is None
    assert await storage.contains(1002) is True
    popped = await storage.pop_if(1002, "keep")
    assert popped is not None
    assert popped.wait_id == "keep"
    assert await storage.contains(1002) is False


@pytest.mark.asyncio
async def test_live_redis_ttl(redis) -> None:
    client, prefix = redis
    storage = RedisInputStorage(client, key_prefix=prefix, ttl=2)
    await storage.set(1003, WaitRecord(wait_id="ttl", created_at=1.0))
    ttl = await client.ttl(f"{prefix}1003")
    assert 0 < ttl <= 2
    await asyncio.sleep(2.2)
    assert await storage.contains(1003) is False


@pytest.mark.asyncio
async def test_live_session_wait_feed_with_redis(storage: RedisInputStorage) -> None:
    session = SessionManager(storage, WaitRegistry())
    chat_id = 4242
    task = asyncio.create_task(session.start_waiting(chat_id, timeout=2, filter=None))
    await asyncio.sleep(0)
    assert await storage.contains(chat_id) is True

    msg = make_message(chat_id, message_id=7)
    assert await session.feed(msg) is True
    assert await task is msg
    assert await storage.contains(chat_id) is False


@pytest.mark.asyncio
async def test_live_overwrite_cleans_redis_marker(storage: RedisInputStorage) -> None:
    session = SessionManager(storage, WaitRegistry())
    chat_id = 5151
    first = asyncio.create_task(session.start_waiting(chat_id, timeout=3, filter=None))
    for _ in range(50):
        if await storage.contains(chat_id):
            break
        await asyncio.sleep(0.01)
    else:
        raise AssertionError("first wait never registered in Redis")

    second = asyncio.create_task(session.start_waiting(chat_id, timeout=3, filter=None))
    assert await first is None

    for _ in range(50):
        if await storage.contains(chat_id):
            break
        await asyncio.sleep(0.01)
    else:
        raise AssertionError("second wait missing from Redis after overwrite")

    msg = make_message(chat_id, message_id=9)
    assert await session.feed(msg) is True
    assert await second is msg
    assert await storage.contains(chat_id) is False


@pytest.mark.asyncio
async def test_live_setup_input_and_waiter(redis) -> None:
    client, prefix = redis
    dp = Dispatcher()
    storage = RedisInputStorage(client, key_prefix=prefix)
    waiter = setup_input(dp, storage=storage, data_key="aiogram_input")
    assert isinstance(waiter, InputWaiter)

    task = asyncio.create_task(waiter.wait(6060, timeout=2))
    await asyncio.sleep(0)
    assert await storage.contains(6060) is True

    middleware = dp.message.outer_middleware._middlewares[0]
    msg = make_message(6060)

    async def handler(event, data):
        return "should-not-run"

    assert await middleware(handler, msg, {}) is None
    assert await task is msg
    assert await storage.contains(6060) is False


@pytest.mark.asyncio
async def test_live_two_connections_share_marker(redis_url: str, redis) -> None:
    client, prefix = redis
    other = Redis.from_url(redis_url, decode_responses=True)
    try:
        writer = RedisInputStorage(client, key_prefix=prefix)
        reader = RedisInputStorage(other, key_prefix=prefix)
        await writer.set(7070, WaitRecord(wait_id="shared", created_at=1.0))
        assert await reader.get(7070) == WaitRecord(wait_id="shared", created_at=1.0)
        assert await reader.pop_if(7070, "shared") is not None
        assert await writer.contains(7070) is False
    finally:
        await other.aclose()
