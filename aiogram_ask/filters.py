from typing import Dict, Tuple
from aiogram.types import Message
from aiogram.filters import BaseFilter
import asyncio

class PendingUserFilter(BaseFilter):
    def __init__(self, pending: Dict[Tuple[int, int], 'asyncio.Future[Message]']):
        self._pending = pending

    async def __call__(self, message: Message) -> bool:
        return (message.from_user and (message.from_user.id, message.chat.id) in self._pending) # pyright: ignore[reportReturnType]