from __future__ import annotations

from typing import Optional

from aiogram import Dispatcher

from .middleware import DEFAULT_DATA_KEY, InputMiddleware
from .registry import WaitRegistry
from .session import SessionManager
from .storage import InputStorage, MemoryInputStorage
from .waiter import InputWaiter


def setup_input(
    dispatcher: Dispatcher,
    /,
    *,
    storage: Optional[InputStorage] = None,
    data_key: str = DEFAULT_DATA_KEY,
) -> InputWaiter:
    """
    Register input waiting once on a Dispatcher.

    Injects ``InputWaiter`` into handler data under ``data_key`` (default:
    ``"input"``) and consumes matching messages only while a wait is active.
    Other messages pass through to FSM and normal handlers.
    """
    if not isinstance(dispatcher, Dispatcher):
        raise TypeError(
            f"dispatcher must be Dispatcher, got {type(dispatcher).__name__}"
        )

    storage = storage or MemoryInputStorage()
    registry = WaitRegistry()
    session = SessionManager(storage, registry)
    waiter = InputWaiter(session)
    InputMiddleware(session, waiter, data_key=data_key).setup(dispatcher)
    return waiter
