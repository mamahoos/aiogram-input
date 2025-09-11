from aiogram.types   import Message
from aiogram.filters import Filter
from .storage        import BaseStorage


class PendingUserFilter(Filter):
    def __init__(self, storage: BaseStorage):
        self._storage = storage

    async def __call__(self, message: Message) -> bool:
        return await self._storage.get(message.chat.id) is not None
