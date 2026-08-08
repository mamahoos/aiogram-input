from __future__ import annotations

import logging
from asyncio import Lock
from typing import Dict, Optional

from .types import PendingWait

logger = logging.getLogger(__name__)


class WaitRegistry:
    """In-process registry for futures and filters bound to a chat wait."""

    def __init__(self) -> None:
        self._waits: Dict[int, PendingWait] = {}
        self._lock = Lock()

    async def get(self, chat_id: int, /) -> Optional[PendingWait]:
        async with self._lock:
            return self._waits.get(chat_id)

    async def set(self, chat_id: int, wait: PendingWait, /) -> Optional[PendingWait]:
        """Register a wait, returning any previous wait for the same chat."""
        async with self._lock:
            previous = self._waits.get(chat_id)
            self._waits[chat_id] = wait
            return previous

    async def pop(self, chat_id: int, /) -> Optional[PendingWait]:
        async with self._lock:
            return self._waits.pop(chat_id, None)

    async def pop_if(self, chat_id: int, wait_id: str, /) -> Optional[PendingWait]:
        async with self._lock:
            wait = self._waits.get(chat_id)
            if wait is None or wait.wait_id != wait_id:
                return None
            return self._waits.pop(chat_id)

    async def contains(self, chat_id: int, /) -> bool:
        async with self._lock:
            return chat_id in self._waits

    @staticmethod
    def cancel_wait(wait: PendingWait, *, chat_id: int) -> None:
        """Abort a wait by resolving it with ``None`` (no CancelledError leak)."""
        future = wait.future
        if future.done():
            return
        future.set_result(None)
        logger.debug("[REGISTRY] Aborted leftover wait chat=%s", chat_id)
