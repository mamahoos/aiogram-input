from __future__ import annotations

import asyncio

import pytest
from aiogram import Dispatcher

from aiogram_input import DEFAULT_DATA_KEY, InputWaiter, setup_input
from aiogram_input.registry import WaitRegistry
from aiogram_input.session import SessionManager
from aiogram_input.storage import MemoryInputStorage
from aiogram_input.types import PendingWait, WaitRecord
from tests.helpers import make_message


@pytest.mark.asyncio
async def test_setup_input_rejects_empty_data_key() -> None:
    dp = Dispatcher()
    with pytest.raises(ValueError, match="data_key"):
        setup_input(dp, data_key="")


@pytest.mark.asyncio
async def test_setup_input_wires_custom_data_key_end_to_end() -> None:
    dp = Dispatcher()
    waiter = setup_input(dp, data_key="aiogram_input")
    middleware = dp.message.outer_middleware._middlewares[0]
    assert middleware._data_key == "aiogram_input"

    async def handler(event, data):
        assert data.get(DEFAULT_DATA_KEY) is not waiter
        assert data["aiogram_input"] is waiter
        return "ok"

    assert await middleware(handler, make_message(1), {"input": "taken"}) == "ok"


@pytest.mark.asyncio
async def test_orphan_storage_marker_is_cleaned_on_feed(
    session: SessionManager, storage: MemoryInputStorage
) -> None:
    await storage.set(55, WaitRecord(wait_id="orphan", created_at=1.0))
    assert await session.feed(make_message(55)) is False
    assert await storage.contains(55) is False


@pytest.mark.asyncio
async def test_feed_when_future_already_done(session: SessionManager) -> None:
    chat_id = 66
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    future.set_result(None)
    await session._registry.set(
        chat_id, PendingWait(wait_id="x", future=future, filter=None)
    )
    await session._storage.set(chat_id, WaitRecord(wait_id="x", created_at=1.0))
    assert await session.feed(make_message(chat_id)) is False


@pytest.mark.asyncio
async def test_registry_pop_missing_returns_none(registry: WaitRegistry) -> None:
    assert await registry.pop(123456) is None


@pytest.mark.asyncio
async def test_cancel_wait_is_noop_when_future_already_done(
    registry: WaitRegistry,
) -> None:
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    future.set_result(None)
    wait = PendingWait(wait_id="done", future=future, filter=None)
    registry.cancel_wait(wait, chat_id=1)
    assert future.result() is None


@pytest.mark.asyncio
async def test_waiter_rejects_non_numeric_timeout() -> None:
    waiter = InputWaiter(SessionManager(MemoryInputStorage(), WaitRegistry()))
    with pytest.raises(TypeError, match="timeout"):
        await waiter.wait(1, timeout="30")  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_waiter_wait_success_path() -> None:
    session = SessionManager(MemoryInputStorage(), WaitRegistry())
    waiter = InputWaiter(session)
    task = asyncio.create_task(waiter.wait(9, timeout=1))
    await asyncio.sleep(0)
    msg = make_message(9)
    assert await session.feed(msg) is True
    assert await task is msg


@pytest.mark.asyncio
async def test_public_exports() -> None:
    import aiogram_input as pkg

    for name in (
        "DEFAULT_DATA_KEY",
        "InputStorage",
        "InputWaiter",
        "MemoryInputStorage",
        "setup_input",
        "__version__",
    ):
        assert hasattr(pkg, name)
    assert pkg.DEFAULT_DATA_KEY == "input"
    assert pkg.__version__ != "0.0.0"
