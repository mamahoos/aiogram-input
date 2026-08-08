from __future__ import annotations

from asyncio import Lock
from typing import Dict, Optional

from ..types import WaitRecord


class MemoryInputStorage:
    """In-memory InputStorage implementation."""

    def __init__(self) -> None:
        self._records: Dict[int, WaitRecord] = {}
        self._lock = Lock()

    async def get(self, chat_id: int, /) -> Optional[WaitRecord]:
        async with self._lock:
            return self._records.get(chat_id)

    async def set(self, chat_id: int, record: WaitRecord, /) -> None:
        async with self._lock:
            self._records[chat_id] = record

    async def pop(self, chat_id: int, /) -> Optional[WaitRecord]:
        async with self._lock:
            return self._records.pop(chat_id, None)

    async def pop_if(self, chat_id: int, wait_id: str, /) -> Optional[WaitRecord]:
        async with self._lock:
            record = self._records.get(chat_id)
            if record is None or record.wait_id != wait_id:
                return None
            return self._records.pop(chat_id)

    async def contains(self, chat_id: int, /) -> bool:
        async with self._lock:
            return chat_id in self._records
