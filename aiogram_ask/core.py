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
    async def ask(self, user_id: int, chat_id: int, timeout: None = None) -> Message:
        ...

    @overload
    async def ask(self, user_id: int, chat_id: int, timeout: float) -> Optional[Message]:
        ...
    
    async def ask(self, user_id: int, chat_id: int, timeout: Optional[float] = None) -> Optional[Message]:
        """
        Wait for the next message from a specific user in a specific chat.
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