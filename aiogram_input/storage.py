from aiogram.types   import Message
from typing          import Optional, Dict
from asyncio         import Future, Lock
from .types          import PendingEntry, FilterObjectType

# ---------- PendingEntryStorage ---------- #

class PendingEntryStorage:
    def __init__(self) -> None:
        self._pending: Dict[int, PendingEntry] = {}
        self._lock = Lock()
    
    async def get(self, chat_id: int, /) -> Optional[PendingEntry]:
        async with self._lock:
            return self._pending.get(chat_id)
    
    async def pop(self, chat_id: int, /) -> Future[Message]:
        async with self._lock:
            return self._pending.pop(chat_id).future

    async def set(self, chat_id: int, /, filter: FilterObjectType, future: Future[Message]) -> None:
        async with self._lock:
            self._pending[chat_id] = PendingEntry(filter, future)
            
    def __contains__(self, chat_id: int, /) -> bool:
        return chat_id in self._pending