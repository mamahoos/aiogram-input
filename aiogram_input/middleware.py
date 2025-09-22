from  typing        import Dict, Callable, Any, Awaitable
from  aiogram.types import Message, TelegramObject
from  aiogram       import BaseMiddleware
from .session       import SessionManager
from .types         import Target

class InputMiddleware(BaseMiddleware):
    """
    Middleware to feed all incoming messages to SessionManager.
    Should be registered in the Router or Dispatcher.
    """
    def __init__(self, session: SessionManager):
        self._session = session

    async def __call__(self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            await self._session.feed(event)
        # TODO: Add support for other event types if needed
        return await handler(event, data)

    def setup(self, target: Target) -> None:
        """Register middleware in the given Router or Dispatcher."""
        target.message.outer_middleware.register(self)