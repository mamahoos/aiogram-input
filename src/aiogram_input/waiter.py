from __future__ import annotations

from typing import Optional, Union

from aiogram.dispatcher.event.handler import FilterObject
from aiogram.types import Message

from .session import SessionManager
from .types import CallbackType


class InputWaiter:
    """Handler-facing API injected by middleware (like FSMContext)."""

    def __init__(self, session: SessionManager) -> None:
        self._session = session

    async def wait(
        self,
        chat_id: int,
        timeout: Union[float, int],
        filter: Optional[CallbackType] = None,
    ) -> Optional[Message]:
        """
        Wait asynchronously for the next matching message in a chat.

        Returns the message, or ``None`` on timeout.
        """
        self._validate_args(chat_id, timeout, filter)
        filter_obj = FilterObject(filter) if filter is not None else None
        return await self._session.start_waiting(chat_id, timeout, filter_obj)

    @staticmethod
    def _validate_args(
        chat_id: int, timeout: Union[float, int], filter: Optional[CallbackType]
    ) -> None:
        if not isinstance(chat_id, int):
            raise TypeError(f"chat_id must be int, got {type(chat_id).__name__}")
        if not isinstance(timeout, (int, float)):
            raise TypeError(
                f"timeout must be float or int, got {type(timeout).__name__}"
            )
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        if filter is not None and not callable(filter):
            raise TypeError(
                f"filter must be callable or None, got {type(filter).__name__}"
            )
