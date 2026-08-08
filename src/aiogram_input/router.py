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
        self.router      = target
        self._session    = session
        self._storage    = storage
        self._middleware = InputMiddleware(session)
        if setup:
            self._setup_middleware()

    def _setup_middleware(self):
        logger.debug("[ROUTER] Setting up input middleware")
        self._middleware.setup(self.router)