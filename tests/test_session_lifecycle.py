from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

import pytest
from aiogram.types import Message

from aiogram_input.registry import WaitRegistry
from aiogram_input.session import SessionManager
from aiogram_input.storage import MemoryInputStorage


def _message(chat_id: int, message_id: int = 1) -> Message:
    msg = MagicMock(spec=Message)
    msg.chat = MagicMock()
    msg.chat.id = chat_id
    msg.message_id = message_id
    return msg


@pytest.fixture
def session() -> SessionManager:
    return SessionManager(MemoryInputStorage(), WaitRegistry())


@pytest.mark.asyncio
async def test_wait_resolves_with_fed_message(session: SessionManager) -> None:
    chat_id = 42
    waiter = asyncio.create_task(session.start_waiting(chat_id, timeout=1, filter=None))
    await asyncio.sleep(0)
    msg = _message(chat_id)
    assert await session.feed(msg) is True
    assert await waiter is msg
    assert await session._storage.contains(chat_id) is False
    assert await session._registry.contains(chat_id) is False


@pytest.mark.asyncio
async def test_timeout_cleans_storage_and_registry(session: SessionManager) -> None:
    chat_id = 7
    result = await session.start_waiting(chat_id, timeout=0.05, filter=None)
    assert result is None
    assert await session._storage.contains(chat_id) is False
    assert await session._registry.contains(chat_id) is False


@pytest.mark.asyncio
async def test_overwrite_aborts_previous_wait_without_leak(
    session: SessionManager,
) -> None:
    chat_id = 99
    first = asyncio.create_task(session.start_waiting(chat_id, timeout=2, filter=None))
    await asyncio.sleep(0)
    second = asyncio.create_task(session.start_waiting(chat_id, timeout=2, filter=None))
    await asyncio.sleep(0)

    assert await first is None

    msg = _message(chat_id, message_id=2)
    assert await session.feed(msg) is True
    assert await second is msg
    assert await session._storage.contains(chat_id) is False
    assert await session._registry.contains(chat_id) is False


@pytest.mark.asyncio
async def test_filter_reject_does_not_consume(session: SessionManager) -> None:
    chat_id = 11

    class Reject:
        async def call(self, _message: Message) -> bool:
            return False

    waiter = asyncio.create_task(
        session.start_waiting(chat_id, timeout=0.2, filter=Reject())  # type: ignore[arg-type]
    )
    await asyncio.sleep(0)
    assert await session.feed(_message(chat_id)) is False
    assert await waiter is None


@pytest.mark.asyncio
async def test_feed_without_pending_is_false(session: SessionManager) -> None:
    assert await session.feed(_message(1)) is False
