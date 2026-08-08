from __future__ import annotations

import asyncio

import pytest

from aiogram_input.registry import WaitRegistry
from aiogram_input.types import PendingWait, WaitRecord
from aiogram_input.storage import MemoryInputStorage


@pytest.mark.asyncio
async def test_registry_pop_if_only_matching_id(registry: WaitRegistry) -> None:
    loop = asyncio.get_running_loop()
    wait = PendingWait(wait_id="w1", future=loop.create_future(), filter=None)
    await registry.set(1, wait)
    assert await registry.pop_if(1, "other") is None
    assert await registry.contains(1) is True
    assert await registry.pop_if(1, "w1") is wait
    assert await registry.contains(1) is False


@pytest.mark.asyncio
async def test_registry_set_returns_previous(registry: WaitRegistry) -> None:
    loop = asyncio.get_running_loop()
    first = PendingWait(wait_id="a", future=loop.create_future(), filter=None)
    second = PendingWait(wait_id="b", future=loop.create_future(), filter=None)
    assert await registry.set(1, first) is None
    assert await registry.set(1, second) is first
    assert await registry.get(1) is second


@pytest.mark.asyncio
async def test_memory_storage_get_set_roundtrip(storage: MemoryInputStorage) -> None:
    record = WaitRecord(wait_id="x", created_at=123.0)
    await storage.set(9, record)
    assert await storage.get(9) == record
    assert await storage.contains(9) is True
    popped = await storage.pop(9)
    assert popped == record
    assert await storage.get(9) is None


@pytest.mark.asyncio
async def test_cancel_wait_resolves_future_with_none(registry: WaitRegistry) -> None:
    loop = asyncio.get_running_loop()
    future: asyncio.Future = loop.create_future()
    wait = PendingWait(wait_id="z", future=future, filter=None)
    registry.cancel_wait(wait, chat_id=1)
    assert future.done()
    assert future.result() is None
