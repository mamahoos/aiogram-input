from aiogram        import Router
from aiogram.types  import Message
from .filters       import PendingUserFilter
from .storage       import BaseStorage, DefaultStorage

def setup_router(storage: BaseStorage):
    router = Router(name="asker")

    @router.message(PendingUserFilter(storage=storage))
    async def _catch_user_reply(message: Message):
        chat_id         = message.chat.id
        filter, future  = await storage.get(chat_id)      # pyright: ignore[reportGeneralTypeIssues]
        if not future.done():
            filter, future = await storage.get(chat_id)   # pyright: ignore[reportGeneralTypeIssues]
            if filter is not None and not await filter(message):
                return
            future.set_result(message)
            await storage.pop(chat_id)
    
    return router