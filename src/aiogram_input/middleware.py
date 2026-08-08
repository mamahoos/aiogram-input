from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, Dispatcher
from aiogram.types import Message, TelegramObject

from .session import SessionManager
from .waiter import InputWaiter

DEFAULT_DATA_KEY = "input"


class InputMiddleware(BaseMiddleware):
    """
    Feed pending waits and inject ``InputWaiter`` into handler data.

    Register only on Dispatcher so every router shares one waiter instance.
    """

    def __init__(
        self,
        session: SessionManager,
        waiter: InputWaiter,
        *,
        data_key: str = DEFAULT_DATA_KEY,
    ) -> None:
        if not data_key:
            raise ValueError("data_key must be a non-empty string")
        self._session = session
        self._waiter = waiter
        self._data_key = data_key

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data[self._data_key] = self._waiter
        if isinstance(event, Message):
            if await self._session.feed(event):
                return None
        return await handler(event, data)

    def setup(self, dispatcher: Dispatcher) -> None:
        dispatcher.message.outer_middleware.register(self)
