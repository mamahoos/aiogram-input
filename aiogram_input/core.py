import asyncio, logging
from typing import Optional, TYPE_CHECKING, Union

from aiogram.types   import Message
from aiogram.filters import Filter
from aiogram         import Router

from .router  import setup_router
from .storage import BaseStorage, DefaultStorage

# ---------- Logging ---------- #

logger = logging.getLogger(__name__)

# ---------- InputManager ----------- #

class InputManager:
    def __init__(self, storage: BaseStorage = DefaultStorage()):
        self._storage: BaseStorage      = storage
        self._router : Optional[Router] = None

    @property
    def router(self) -> Router:
        """
        Lazily initialize and return the router for handling user replies.
        """
        if self._router is None:
            self._router = setup_router(self._storage)
        return self._router

    async def input(
        self, 
        chat_id: int, 
        timeout: Union[float, int], 
        filter: Optional[Filter] = None
    ) -> Optional[Message]:
        """
        Wait asynchronously for the next incoming message in a specific chat.

        This coroutine suspends execution until a message matching the 
        given ``filter`` (if provided) arrives in the target ``chat_id``.
        It uses an internal pending queue to resolve awaiting coroutines 
        once the message is dispatched.

        Args:
            chat_id (int): The unique identifier of the chat to listen on.
            timeout (float | int): Maximum number of seconds to wait.
            filter (Optional[Filter]): Optional aiogram filter applied 
                to incoming messages before resolving.

        Returns:
            Optional[Message]:
                - ``Message`` if received within the timeout window.
                - ``None`` if no message arrived before timeout.

        Raises:
            asyncio.CancelledError: If the waiting task is cancelled.
            Exception: For unexpected runtime errors.
        """
        self._validate_args(chat_id, timeout)

        loop = asyncio.get_running_loop()
        future: asyncio.Future[Message] = loop.create_future()
        self._storage.set(chat_id, filter=filter, future=future)

        logger.debug(f"[INPUT] Waiting for message in chat={chat_id}, timeout={timeout}, filter={filter}")

        try:
            result = await asyncio.wait_for(future, timeout=timeout)
            logger.debug(f"[INPUT] Received message in chat={chat_id}")
            return result
        except asyncio.TimeoutError:
            logger.debug(f"[INPUT] Timeout for chat={chat_id}")
            self._storage.pop(chat_id)
            return None

    # ---------- Private Helpers ----------

    @staticmethod
    def _validate_args(chat_id: int, timeout: Optional[float]) -> None:
        """Runtime validation in case type-checker is not used."""
        if not TYPE_CHECKING:
            if not isinstance(chat_id, int):
                raise TypeError(f"chat_id must be int, got {type(chat_id).__name__}")
            if not isinstance(timeout, (int, float)):
                raise TypeError(f"timeout must be float or int or None, got {type(timeout).__name__}")
