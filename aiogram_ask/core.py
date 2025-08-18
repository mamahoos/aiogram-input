import asyncio
import logging
from typing import Dict, Tuple, Optional, TYPE_CHECKING, overload

from aiogram.types import Message
from aiogram import Router
from .router import setup_router

# ---------- Logging ---------- #

logger = logging.getLogger(__name__)

# ---------- Asker ----------- #

class Asker:
    def __init__(self):
        self._pending: Dict[Tuple[int, int], 'asyncio.Future[Message]'] = {}
        self._router: Optional[Router] = None

    @property
    def router(self) -> Router:
        """
        Lazily initialize and return the router for handling user replies.
        """
        if self._router is None:
            self._router = setup_router(self._pending)
        return self._router
    
    @overload
    async def ask(self, user_id: int, chat_id: int) -> Message:
        ...

    @overload
    async def ask(self, user_id: int, chat_id: int, timeout: float) -> Optional[Message]:
        ...
    
    async def ask(self, user_id: int, chat_id: int, timeout: Optional[float] = None) -> Optional[Message]:
        """
        Wait for the next incoming message from a specific user in a specific chat.

        This coroutine suspends execution until the next message is received 
        from the given ``user_id`` inside the given ``chat_id``. 
        It uses an internal pending queue to resolve awaiting coroutines 
        when the message arrives.

        Args:
            user_id (int): The unique identifier of the user to listen for.
            chat_id (int): The unique identifier of the chat where the message is expected.
            timeout (Optional[float], default=None): 
                Maximum time in seconds to wait for the message. 
                - If ``None``: waits indefinitely until a message arrives.
                - If a positive float is given: waits up to that duration, 
                  otherwise returns ``None`` if timeout is reached.

        Returns:
            Optional[Message]: 
                - If ``timeout`` is ``None``: always returns a ``Message`` once received.  
                - If ``timeout`` is a float: returns ``Message`` if received within the duration, 
                  otherwise returns ``None`` after timeout.

        Raises:
            asyncio.CancelledError: If the waiting task is cancelled.
            Exception: Any unexpected error raised during message dispatching 
                       (not including ``TimeoutError``, which is handled internally).

        Example:
            ```python
            msg = await asker.ask(user_id=123, chat_id=456, timeout=30)
            if msg is None:
                print("No reply received within 30 seconds.")
            else:
                print(f"User replied: {msg.text}")
            ```
        """
        self._validate_args(user_id, chat_id, timeout)
        
        loop = asyncio.get_running_loop()
        fut: asyncio.Future[Message] = loop.create_future()
        self._pending[(user_id, chat_id)] = fut

        logger.debug(f"[ASK] Waiting for message from user={user_id}, chat={chat_id}, timeout={timeout}")

        try:
            result = await asyncio.wait_for(fut, timeout=timeout)
            logger.debug(f"[ASK] Got message from user={user_id}, chat={chat_id}: {result.text!r}")
            return result
        except asyncio.TimeoutError:
            logger.debug(f"[ASK] Timeout for user={user_id}, chat={chat_id}")
            self._pending.pop((user_id, chat_id), None)
            return None
        
     # ---------- Private Helpers ----------

    @staticmethod
    def _validate_args(user_id: int, chat_id: int, timeout: Optional[float]) -> None:
        """Runtime validation in case type-checker is not used."""
        if not TYPE_CHECKING:
            if not isinstance(user_id, int):
                raise TypeError(f"user_id must be int, got {type(user_id).__name__}")
            if not isinstance(chat_id, int):
                raise TypeError(f"chat_id must be int, got {type(chat_id).__name__}")
            if timeout is not None and not isinstance(timeout, (int, float)):
                raise TypeError(f"timeout must be float or int or None, got {type(timeout).__name__}")