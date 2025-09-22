import logging

from typing import Optional, Union, TYPE_CHECKING

from  aiogram.types   import Message
from  aiogram         import Router, Dispatcher
from  aiogram.dispatcher.event.handler import FilterObject

from .router  import RouterManager
from .storage import PendingEntryStorage
from .session import SessionManager
from . types  import CallbackType

# ---------- Logging ---------- #

logger = logging.getLogger(__name__)

# ---------- InputManager ----------- #

class InputManager:
    def __init__(self, target: Union[Router, Dispatcher], /) -> None:
        """Initialize InputManager with a Router or Dispatcher."""
        if not TYPE_CHECKING:
            self._validate_target(target)
        self._storage = PendingEntryStorage()
        self._session = SessionManager(self._storage)
        self._router  = RouterManager(target, self._session, self._storage, setup=True)

    async def input(
        self, 
        chat_id: int, 
        timeout: Union[float, int], 
        filter: Optional[CallbackType] = None
    ) -> Optional[Message]:
        """
        Wait asynchronously for the next message in a specific chat.

        This coroutine suspends until either:
        - a message from the given ``chat_id`` passes the optional ``filter``,
        - or the ``timeout`` is reached.

        Args:
            chat_id (int): Unique identifier of the chat to listen on.
            timeout (float | int): Maximum seconds to wait for a message.
            filter (Optional[CallbackType]): Optional callback to validate 
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
        if not TYPE_CHECKING:
            self._validate_args(chat_id, timeout, filter)
        
        filter_obj = FilterObject(filter) if filter is not None else None
        result     = await self._session.start_waiting(chat_id, timeout, filter_obj)
        
        return result

    # ---------- Private Helpers ----------

    @staticmethod
    def _validate_args(chat_id: int, timeout: Union[float, int], filter: Optional[CallbackType]) -> None:
        if not isinstance(chat_id, int):
            raise TypeError(f"chat_id must be int, got {type(chat_id).__name__}")
        if not isinstance(timeout, (int, float)):
            raise TypeError(f"timeout must be float or int, got {type(timeout).__name__}")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        if filter is not None and not callable(filter):
            raise TypeError(f"filter must be callable or None, got {type(filter).__name__}")
        
    @staticmethod  
    def _validate_target(target: Union[Router, Dispatcher]) -> None:
        if not isinstance(target, (Router, Dispatcher)):
            raise TypeError(f"target must be Router or Dispatcher, got {type(target).__name__}")