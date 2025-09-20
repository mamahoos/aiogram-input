import logging
from   aiogram       import Router
from   aiogram.types import Message
from  .filters       import PendingUserFilter
from  .storage       import PendingEntryStorage
from  .session       import SessionManager
from   typing        import Optional

# ---------- Logging ---------- #

logger = logging.getLogger(__name__)

# ---------- RouterManager ---------- #

class RouterManager:
    def __init__(self, name: Optional[str], session: SessionManager, storage: PendingEntryStorage):
        DEFAULT_NAME  = f"aiogram_input[{hex(id(storage))}]"
        self.router   = Router(name=name or DEFAULT_NAME)
        self._session = session
        self._storage = storage
        self._setup_filters()
        self._setup_handlers()

    def _setup_handlers(self):
        logger.debug("[ROUTER] Setting up message handler for pending users")
        @self.router.message()
        async def __catch_user_message(message: Message):
            await self._session.feed(message)

    def _setup_filters(self):
        logger.debug("[ROUTER] Setting up PendingUserFilter")
        self.router.message.filter(PendingUserFilter(storage=self._storage))