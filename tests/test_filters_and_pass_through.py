from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

import pytest
from aiogram import Dispatcher
from aiogram.types import CallbackQuery

from aiogram_input import InputWaiter, setup_input
from aiogram_input.middleware import DEFAULT_DATA_KEY, InputMiddleware
from aiogram_input.session import SessionManager
from .helpers import make_message


class AcceptOnce:
    def __init__(self) -> None:
        self.calls = 0

    async def call(self, _message) -> bool:
        self.calls += 1
        return True


class RejectAll:
    async def call(self, _message) -> bool:
        return False


@pytest.mark.asyncio
async def test_accepting_filter_consumes_message(session: SessionManager) -> None:
    filt = AcceptOnce()
    task = asyncio.create_task(
        session.start_waiting(1, timeout=1, filter=filt)  # type: ignore[arg-type]
    )
    await asyncio.sleep(0)
    msg = make_message(1)
    assert await session.feed(msg) is True
    assert await task is msg
    assert filt.calls == 1


@pytest.mark.asyncio
async def test_rejecting_filter_keeps_wait_alive_until_timeout(
    session: SessionManager,
) -> None:
    task = asyncio.create_task(
        session.start_waiting(2, timeout=0.1, filter=RejectAll())  # type: ignore[arg-type]
    )
    await asyncio.sleep(0)
    assert await session.feed(make_message(2)) is False
    assert await session._storage.contains(2) is True
    assert await task is None
    assert await session._storage.contains(2) is False


@pytest.mark.asyncio
async def test_non_message_event_passes_through_with_injection() -> None:
    dp = Dispatcher()
    waiter = setup_input(dp)
    middleware = InputMiddleware(waiter._session, waiter)
    event = MagicMock(spec=CallbackQuery)
    seen = {}

    async def handler(evt, data):
        seen["event"] = evt
        seen["input"] = data.get(DEFAULT_DATA_KEY)
        return "cb"

    assert await middleware(handler, event, {}) == "cb"
    assert seen["event"] is event
    assert isinstance(seen["input"], InputWaiter)


@pytest.mark.asyncio
async def test_unmatched_message_reaches_handler_fsm_coexistence() -> None:
    """No active wait => middleware must not swallow the update."""
    dp = Dispatcher()
    waiter = setup_input(dp)
    middleware = InputMiddleware(waiter._session, waiter)
    reached = False

    async def handler(event, data):
        nonlocal reached
        reached = True
        assert data[DEFAULT_DATA_KEY] is waiter
        return "handled"

    result = await middleware(handler, make_message(999), {})
    assert result == "handled"
    assert reached is True
