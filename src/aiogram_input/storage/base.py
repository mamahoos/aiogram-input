from __future__ import annotations

from typing import Optional, Protocol, runtime_checkable

from ..types import WaitRecord


@runtime_checkable
class InputStorage(Protocol):
    """Persisted wait markers. Futures never live here (Redis-safe boundary)."""

    async def get(self, chat_id: int, /) -> Optional[WaitRecord]:
        """Return the wait marker for ``chat_id``, if any."""

    async def set(self, chat_id: int, record: WaitRecord, /) -> None:
        """Create or replace the wait marker for ``chat_id``."""

    async def pop(self, chat_id: int, /) -> Optional[WaitRecord]:
        """Remove and return the wait marker for ``chat_id``, if any."""

    async def pop_if(self, chat_id: int, wait_id: str, /) -> Optional[WaitRecord]:
        """Remove the marker only when it belongs to ``wait_id``."""

    async def contains(self, chat_id: int, /) -> bool:
        """Return whether ``chat_id`` currently has a wait marker."""
