from typing             import Dict, Tuple
from aiogram.types      import Message
from aiogram.filters    import Filter
from .storage           import BaseStorage


class PendingUserFilter(Filter):
    def __init__(self, storage: BaseStorage):
        self._storage = storage

    async def __call__(self, message: Message) -> bool:
        data = self._storage.get(message.chat.id)
        if data is None:
            return False
        filter, future = data
        return True if filter is None else bool(await filter(message))