from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

import pytest
from aiogram import Dispatcher
from aiogram.types import Message

from aiogram_input import InputWaiter, MemoryInputStorage, setup_input
from aiogram_input.middleware import DEFAULT_DATA_KEY, InputMiddleware


def _message(chat_id: int) -> Message:
    msg = MagicMock(spec=Message)
    msg.chat = MagicMock()
    msg.chat.id = chat_id
    msg.message_id = 1
    return msg


@pytest.mark.asyncio
async def test_setup_input_requires_dispatcher() -> None:
    with pytest.raises(TypeError, match="Dispatcher"):
        setup_input(object())  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_middleware_injects_waiter_and_passes_through() -> None:
    dp = Dispatcher()
    waiter = setup_input(dp, storage=MemoryInputStorage())
    assert isinstance(waiter, InputWaiter)

    middleware = InputMiddleware(waiter._session, waiter)
    called = False

    async def handler(event, data):
        nonlocal called
        called = True
        assert data[DEFAULT_DATA_KEY] is waiter
        return "ok"

    result = await middleware(handler, _message(1), {})
    assert result == "ok"
    assert called is True


@pytest.mark.asyncio
async def test_custom_data_key_avoids_name_collision() -> None:
    dp = Dispatcher()
    waiter = setup_input(dp, data_key="aiogram_input")
    middleware = InputMiddleware(waiter._session, waiter, data_key="aiogram_input")

    async def handler(event, data):
        assert data["input"] == "user-dep"
        assert data["aiogram_input"] is waiter
        return "ok"

    assert await middleware(handler, _message(1), {"input": "user-dep"}) == "ok"


@pytest.mark.asyncio
async def test_empty_data_key_rejected() -> None:
    dp = Dispatcher()
    waiter = setup_input(dp)
    with pytest.raises(ValueError, match="data_key"):
        InputMiddleware(waiter._session, waiter, data_key="")


@pytest.mark.asyncio
async def test_middleware_consumes_matching_wait() -> None:
    dp = Dispatcher()
    waiter = setup_input(dp)
    session = waiter._session
    chat_id = 5

    wait_task = asyncio.create_task(session.start_waiting(chat_id, timeout=1, filter=None))
    await asyncio.sleep(0)

    middleware = InputMiddleware(session, waiter)
    handler_called = False

    async def handler(event, data):
        nonlocal handler_called
        handler_called = True
        return "should-not-run"

    msg = _message(chat_id)
    result = await middleware(handler, msg, {})
    assert result is None
    assert handler_called is False
    assert await wait_task is msg
