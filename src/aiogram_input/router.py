from __future__ import annotations

import logging

from .middleware import InputMiddleware
from .session import SessionManager
from .types import Target

logger = logging.getLogger(__name__)


class RouterManager:
    def __init__(
        self, target: Target, session: SessionManager, setup: bool = True
    ) -> None:
        self.router = target
        self._session = session
        self._middleware = InputMiddleware(session)
        if setup:
            self._setup_middleware()

    def _setup_middleware(self) -> None:
        logger.debug("[ROUTER] Setting up input middleware")
        self._middleware.setup(self.router)
