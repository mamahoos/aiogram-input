from aiogram.types   import Message
from aiogram.filters import Filter
from .storage        import PendingEntryStorage


class PendingUserFilter(Filter):
    def __init__(self, storage: PendingEntryStorage):
        self._storage = storage

    async def __call__(self, message: Message) -> bool:
        chat_id = message.chat.id
        return (chat_id in self._storage)