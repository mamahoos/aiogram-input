import asyncio, logging
from typing          import Optional, Union
from aiogram.types   import Message
from aiogram.filters import Filter
from .storage        import PendingEntryStorage

# ---------- Logging ---------- #

logger = logging.getLogger(__name__)

# ---------- SessionManager ---------- #

class SessionManager:
    """
    Manages waiting sessions for user input.
    Decouples storage, future creation, timeout handling, and message feeding.
    """

    def __init__(self, storage: PendingEntryStorage):
        self._storage = storage

    # ---------- Public API ---------- #

    async def start_waiting(
        self,
        chat_id: int,
        timeout: Union[int, float],
        filter: Optional[Filter],
    ) -> Optional[Message]:
        """Start waiting for a user's input in a chat."""
        future: asyncio.Future[Message] = self._create_future()
        await self._register_pending(chat_id, filter, future)
        
        filter_name = filter.__class__.__name__ if filter else str(None)
        logger.debug(f"[SESSION] Start waiting chat={chat_id}, timeout={timeout}, filter={filter_name}")

        try:
            message = await self._await_future(future, timeout)
            logger.debug(f"[SESSION] Success chat={chat_id}, message_id={message.message_id}")
            return message
        except asyncio.TimeoutError:
            logger.warning(f"[SESSION] Timeout chat={chat_id}")
            return None
        finally:
            await self._cleanup(chat_id)

    async def feed(self, message: Message) -> None:
        """Feed an incoming message into the waiting session if valid."""
        chat_id = message.chat.id
        logger.debug(f"[SESSION] Received message chat={chat_id}, message_id={message.message_id}")
        
        entry = await self._storage.get(chat_id)
        if not entry:
            logger.debug(f"[SESSION] No pending entry chat={chat_id}")
            return

        filter, future = entry.filter, entry.future
        if filter and not await filter(message):
            filter_name = filter.__class__.__name__
            logger.debug(f"[SESSION] Filter rejected message chat={chat_id}, filter={filter_name}")
            return

        if not future.done():
            future.set_result(message)
            logger.debug(f"[SESSION] Future resolved chat={chat_id}, message_id={message.message_id}")

    # ---------- Private Helpers ---------- #

    @staticmethod
    def _create_future() -> asyncio.Future:
        """Create a new asyncio future bound to current event loop."""
        loop = asyncio.get_running_loop()
        return loop.create_future()

    @staticmethod
    async def _await_future(
        future: asyncio.Future[Message], timeout: Union[int, float]
    ) -> Message:
        """Wait for the future to complete or timeout."""
        return await asyncio.wait_for(future, timeout=timeout)

    async def _register_pending(
        self, chat_id: int, filter: Optional[Filter], future: asyncio.Future[Message]
    ) -> None:
        """Register a pending entry for the given chat."""
        await self._storage.set(chat_id, filter=filter, future=future)
        
    async def _cleanup(self, chat_id: int) -> None:
        """Ensure pending entry is removed from storage."""
        removed = await self._storage.pop(chat_id)
        if not removed:
            logger.debug(f"[SESSION] Cleanup found nothing chat={chat_id}")
