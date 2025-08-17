from aiogram import Router
from aiogram.types import Message
from .filters import PendingUserFilter
from typing import Dict, Tuple
import asyncio

def setup_router(pending: Dict[Tuple[int, int], 'asyncio.Future[Message]']):
    router = Router(name="asker")

    @router.message(PendingUserFilter(pending))
    async def _catch_user_reply(message: Message):
        key = (message.from_user.id, message.chat.id)
        fut = pending[key]
        if not fut.done():
            fut.set_result(message)
            pending.pop(key, None)
    
    return router