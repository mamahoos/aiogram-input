from aiogram.types   import Message
from .               import BaseStorage
from typing          import Optional, Dict, NamedTuple
from asyncio         import Future
from threading       import Lock
from aiogram.filters import Filter

class PendingEntry(NamedTuple):
    filter: Optional[Filter]
    future: Future[Message]

class DefaultStorage(BaseStorage):
    def __init__(self) -> None:
        self._pending: Dict[int, PendingEntry] = {}
        self._lock = Lock()
    
    def get(self, chat_id: int, /) -> Optional[PendingEntry]: # pyright: ignore[reportIncompatibleMethodOverride]
        with self._lock:
            return self._pending.get(chat_id)
    
    def pop(self, chat_id: int, /) -> Future[Message]:
        with self._lock:
            return self._pending.pop(chat_id).future

    def set(self, chat_id: int, /, filter: Optional[Filter], future: Future[Message]) -> None:
        with self._lock:
            self._pending[chat_id] = PendingEntry(filter, future)