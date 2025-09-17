import logging

from typing    import Optional, Union
from functools import cached_property

from  aiogram.types   import Message
from  aiogram.filters import Filter
from  aiogram         import Router

from .router  import RouterManager
from .storage import PendingEntryStorage
from .session import SessionManager

# ---------- Logging ---------- #

logger = logging.getLogger(__name__)

# ---------- InputManager ----------- #

class InputManager:
    def __init__(self, *, name: Optional[str] = None):
        self._storage = PendingEntryStorage()
        self._session = SessionManager(self._storage)
        self._router  = RouterManager(name, self._session, self._storage)

    @cached_property
    def router(self) -> Router:
        return self._router.router

    async def input(
        self, 
        chat_id: int, 
        timeout: Union[float, int], 
        filter: Optional[Filter] = None
    ) -> Optional[Message]:
        """
        Wait asynchronously for the next message in a specific chat.

        This coroutine suspends until either:
        - a message from the given ``chat_id`` passes the optional ``filter``,
        - or the ``timeout`` is reached.

        Args:
            chat_id (int): Unique identifier of the chat to listen on.
            timeout (float | int): Maximum seconds to wait for a message.
            filter (Optional[Filter]): Optional aiogram filter to validate 
                incoming messages.

        Returns:
            Optional[Message]: 
                The received message if matched, otherwise ``None`` on timeout.

        Raises:
            TypeError: If arguments are of invalid type.
            ValueError: If ``timeout`` is not positive.
            asyncio.CancelledError: If the waiting task is cancelled.
            Exception: For unexpected runtime errors.
        """
        self._validate_args(chat_id, timeout, filter)
        result = await self._session.start_waiting(chat_id, timeout, filter)
        return result

    # ---------- Private Helpers ----------

    @staticmethod
    def _validate_args(chat_id: int, timeout: Union[float, int], filter: Optional[Filter]) -> None:
        if not isinstance(chat_id, int):
            raise TypeError(f"chat_id must be int, got {type(chat_id).__name__}")
        if not isinstance(timeout, (int, float)):
            raise TypeError(f"timeout must be float or int, got {type(timeout).__name__}")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        if filter is not None and not isinstance(filter, Filter):
            raise TypeError(f"filter must be Filter or None, got {type(filter).__name__}")
