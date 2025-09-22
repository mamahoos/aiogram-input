import logging
from   aiogram       import Router, Dispatcher
from   aiogram.types import Message
from  .middleware    import InputMiddleware
from  .storage       import PendingEntryStorage
from  .session       import SessionManager
from  .types         import Target
from   typing        import Optional, Union

# ---------- Logging ---------- #

logger = logging.getLogger(__name__)

# ---------- RouterManager ---------- #

class RouterManager:
    def __init__(self, target: Target, session: SessionManager, storage: PendingEntryStorage, setup: bool = True) -> None:
        self.router   = target
        self._session = session
        self._storage = storage
        if setup:
            self._setup_middleware()
            self._setup_handlers()

    def _setup_handlers(self):
        logger.debug("[ROUTER] Setting up message handler for pending users")
        @self.router.message()
        async def __catch_user_message(message: Message):
            await self._session.feed(message)

    def _setup_middleware(self):
        logger.debug("[ROUTER] Setting up input middleware")
        InputMiddleware(self._session).setup(self.router)