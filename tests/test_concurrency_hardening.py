from __future__ import annotations

import asyncio

import pytest

from aiogram_input.registry import WaitRegistry
from aiogram_input.session import SessionManager
from aiogram_input.storage import MemoryInputStorage, RedisInputStorage
from aiogram_input.types import PendingWait, WaitRecord
from tests.helpers import make_message


class BoomFilter:
    async def call(self, _message) -> bool:
        raise RuntimeError("filter exploded")


@pytest.mark.asyncio
async def test_filter_exception_does_not_consume(session: SessionManager) -> None:
    chat_id = 1
    task = asyncio.create_task(
        session.start_waiting(chat_id, timeout=0.2, filter=BoomFilter())  # type: ignore[arg-type]
    )
    await asyncio.sleep(0)
    assert await session.feed(make_message(chat_id)) is False
    assert await task is None


@pytest.mark.asyncio
async def test_resolve_if_rejects_stale_wait_id(registry: WaitRegistry) -> None:
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    await registry.set(
        1, PendingWait(wait_id="current", future=future, filter=None)
    )
    assert await registry.resolve_if(1, "stale", make_message(1)) is False
    assert not future.done()
    assert await registry.resolve_if(1, "current", make_message(1)) is True
    assert future.done()
    assert future.result().message_id == 1


@pytest.mark.asyncio
async def test_concurrent_feeds_only_one_consumes(session: SessionManager) -> None:
    chat_id = 88
    task = asyncio.create_task(session.start_waiting(chat_id, timeout=2, filter=None))
    await asyncio.sleep(0)
    results = await asyncio.gather(
        session.feed(make_message(chat_id, message_id=1)),
        session.feed(make_message(chat_id, message_id=2)),
    )
    assert results.count(True) == 1
    assert results.count(False) == 1
    got = await task
    assert got is not None
    assert got.message_id in {1, 2}


@pytest.mark.asyncio
async def test_redis_corrupt_payload_is_dropped() -> None:
    from fakeredis import FakeAsyncRedis

    redis = FakeAsyncRedis(decode_responses=True)
    storage = RedisInputStorage(redis, key_prefix="bad:")
    await redis.set("bad:1", "{not-json")
    assert await storage.get(1) is None
    assert await redis.exists("bad:1") == 0
    await redis.aclose()


@pytest.mark.asyncio
async def test_redis_rejects_empty_key_prefix() -> None:
    from fakeredis import FakeAsyncRedis

    with pytest.raises(ValueError, match="key_prefix"):
        RedisInputStorage(FakeAsyncRedis(), key_prefix="")


@pytest.mark.asyncio
async def test_feed_after_overwrite_goes_to_latest_wait(
    session: SessionManager,
) -> None:
    chat_id = 77
    first = asyncio.create_task(session.start_waiting(chat_id, timeout=2, filter=None))
    await asyncio.sleep(0)
    second = asyncio.create_task(session.start_waiting(chat_id, timeout=2, filter=None))
    assert await first is None
    msg = make_message(chat_id, message_id=9)
    assert await session.feed(msg) is True
    assert await second is msg
