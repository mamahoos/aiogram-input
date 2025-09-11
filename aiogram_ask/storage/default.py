from aiogram.types   import Message
from .               import BaseStorage
from typing          import Optional, Dict, NamedTuple
from asyncio         import Future
from aiogram.filters import Filter

class StorageArgs(NamedTuple):
    filter: Optional[Filter]
    future: Future[Message]

class DefaultStorage(BaseStorage):
    def __init__(self) -> None:
        self._pending: Dict[int, StorageArgs] = {}
    
    def get(self, chat_id: int, /) -> Optional[StorageArgs]: # pyright: ignore[reportIncompatibleMethodOverride]
        return self._pending.get(chat_id)
    
    def pop(self, chat_id: int, /) -> Future[Message]:
        return self._pending.pop(chat_id)[1]

    def set(self, chat_id: int, /, filter: Optional[Filter], future: Future[Message]) -> None:
        self._pending[chat_id] = StorageArgs(filter, future)
        