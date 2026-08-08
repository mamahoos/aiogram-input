from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional, Union

from aiogram import Dispatcher, Router
from aiogram.dispatcher.event.handler import FilterObject
from aiogram.types import Message

from .registry import WaitRegistry
from .router import RouterManager
from .session import SessionManager
from .storage import MemoryInputStorage
from .types import CallbackType

logger = logging.getLogger(__name__)


class InputManager:
    """Compatibility facade over storage + registry + session (3.x API)."""

    def __init__(self, target: Union[Router, Dispatcher], /) -> None:
        """Initialize InputManager with a Router or Dispatcher."""
        if not TYPE_CHECKING:
            self._validate_target(target)
        self._storage = MemoryInputStorage()
        self._registry = WaitRegistry()
        self._session = SessionManager(self._storage, self._registry)
        self._router = RouterManager(target, self._session, setup=True)

    async def input(
        self,
        chat_id: int,
        timeout: Union[float, int],
        filter: Optional[CallbackType] = None,
    ) -> Optional[Message]:
        """
        Wait asynchronously for the next message in a specific chat.

        This coroutine suspends until either:
        - a message from the given ``chat_id`` passes the optional ``filter``,
        - or the ``timeout`` is reached.
        """
        if not TYPE_CHECKING:
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

    @staticmethod
    def _validate_target(target: Union[Router, Dispatcher]) -> None:
        if not isinstance(target, (Router, Dispatcher)):
            raise TypeError(
                f"target must be Router or Dispatcher, got {type(target).__name__}"
            )
