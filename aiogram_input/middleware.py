from aiogram.types import Message
from .session      import SessionManager
from .types        import Target

class InputMiddleware:
    """
    Middleware to feed all incoming messages to SessionManager.
    Ensures pending inputs are resolved even if Router/Handlers exist.
    """
    def __init__(self, session: SessionManager):
        self._session = session

    async def __call__(self, handler, event, data):
        if isinstance(event, Message):
            await self._session.feed(event)
        return await handler(event, data)

    def setup(self, target: Target) -> None:
        target.message.outer_middleware.register(self)