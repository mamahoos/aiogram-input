from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

import pytest
from aiogram.types import Message

from aiogram_input import MemoryInputStorage, setup_input
from aiogram_input.registry import WaitRegistry
from aiogram_input.session import SessionManager
from aiogram_input.types import WaitRecord
from aiogram_input.waiter import InputWaiter
from aiogram import Dispatcher


def _message(chat_id: int, message_id: int = 1) -> Message:
    msg = MagicMock(spec=Message)
    msg.chat = MagicMock()
    msg.chat.id = chat_id
    msg.message_id = message_id
    return msg


@pytest.mark.asyncio
async def test_waiter_validation() -> None:
    waiter = InputWaiter(SessionManager(MemoryInputStorage(), WaitRegistry()))
    with pytest.raises(TypeError, match="chat_id"):
        await waiter.wait("1", timeout=1)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="positive"):
        await waiter.wait(1, timeout=0)
    with pytest.raises(TypeError, match="filter"):
        await waiter.wait(1, timeout=1, filter=object())  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_memory_storage_pop_if_is_wait_id_scoped() -> None:
    storage = MemoryInputStorage()
    await storage.set(1, WaitRecord(wait_id="a", created_at=1.0))
    assert await storage.pop_if(1, "b") is None
    assert await storage.contains(1) is True
    record = await storage.pop_if(1, "a")
    assert record is not None
    assert record.wait_id == "a"
    assert await storage.contains(1) is False


@pytest.mark.asyncio
async def test_isolated_waits_across_chats() -> None:
    session = SessionManager(MemoryInputStorage(), WaitRegistry())
    w1 = asyncio.create_task(session.start_waiting(1, timeout=1, filter=None))
    w2 = asyncio.create_task(session.start_waiting(2, timeout=1, filter=None))
    await asyncio.sleep(0)

    m1 = _message(1, 10)
    m2 = _message(2, 20)
    assert await session.feed(m1) is True
    assert await session.feed(m2) is True
    assert await w1 is m1
    assert await w2 is m2


@pytest.mark.asyncio
async def test_setup_input_default_storage() -> None:
    dp = Dispatcher()
    waiter = setup_input(dp)
    assert isinstance(waiter, InputWaiter)
    task = asyncio.create_task(waiter.wait(3, timeout=1))
    await asyncio.sleep(0)
    msg = _message(3)
    assert await waiter._session.feed(msg) is True
    assert await task is msg
