from __future__ import annotations

import asyncio

import pytest

from aiogram_input.session import SessionManager
from .helpers import make_message


@pytest.mark.asyncio
async def test_rapid_sequential_waits_same_chat_leave_no_residue(
    session: SessionManager,
) -> None:
    chat_id = 77
    for i in range(5):
        task = asyncio.create_task(session.start_waiting(chat_id, timeout=1, filter=None))
        await asyncio.sleep(0)
        msg = make_message(chat_id, message_id=i + 1)
        assert await session.feed(msg) is True
        assert await task is msg

    assert await session._storage.contains(chat_id) is False
    assert await session._registry.contains(chat_id) is False


@pytest.mark.asyncio
async def test_feed_after_resolve_is_ignored(session: SessionManager) -> None:
    chat_id = 12
    task = asyncio.create_task(session.start_waiting(chat_id, timeout=1, filter=None))
    await asyncio.sleep(0)
    first = make_message(chat_id, message_id=1)
    assert await session.feed(first) is True
    assert await task is first
    assert await session.feed(make_message(chat_id, message_id=2)) is False


@pytest.mark.asyncio
async def test_parallel_chats_do_not_cross_feed(session: SessionManager) -> None:
    tasks = {
        chat_id: asyncio.create_task(session.start_waiting(chat_id, timeout=1, filter=None))
        for chat_id in (101, 102, 103)
    }
    await asyncio.sleep(0)

    for chat_id in (101, 102, 103):
        assert await session.feed(make_message(chat_id, message_id=chat_id)) is True

    for chat_id, task in tasks.items():
        result = await task
        assert result is not None
        assert result.chat.id == chat_id
