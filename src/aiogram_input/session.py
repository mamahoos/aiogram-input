from __future__ import annotations

import asyncio
import logging
import time
import uuid
from typing import Optional, Union

from aiogram.types import Message

from .registry import WaitRegistry
from .storage.base import InputStorage
from .types import FilterObjectType, PendingWait, WaitRecord

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages waiting sessions for user input.

    Storage holds Redis-safe markers; WaitRegistry holds futures/filters.
    """

    def __init__(self, storage: InputStorage, registry: WaitRegistry) -> None:
        self._storage = storage
        self._registry = registry

    async def start_waiting(
        self,
        chat_id: int,
        timeout: Union[int, float],
        filter: FilterObjectType,
    ) -> Optional[Message]:
        """Start waiting for a user's input in a chat."""
        wait_id = uuid.uuid4().hex
        future: asyncio.Future[Message] = self._create_future()
        await self._register_pending(chat_id, wait_id, filter, future)

        filter_name = filter.__class__.__name__ if filter else str(None)
        logger.debug(
            "[SESSION] Start waiting chat=%s, timeout=%s, filter=%s, wait_id=%s",
            chat_id,
            timeout,
            filter_name,
            wait_id,
        )

        try:
            message = await self._await_future(future, timeout)
            logger.debug(
                "[SESSION] Success chat=%s, message_id=%s",
                chat_id,
                message.message_id,
            )
            return message
        except asyncio.TimeoutError:
            logger.warning("[SESSION] Timeout chat=%s", chat_id)
            return None
        except asyncio.CancelledError:
            logger.debug("[SESSION] Cancelled chat=%s", chat_id)
            raise
        finally:
            await self._cleanup(chat_id, wait_id)

    async def feed(self, message: Message) -> bool:
        """
        Feed an incoming message into the waiting session if valid.

        Returns True if the message was consumed by a waiting session.
        """
        chat_id = message.chat.id
        logger.debug(
            "[SESSION] Received message chat=%s, message_id=%s",
            chat_id,
            message.message_id,
        )

        if not await self._storage.contains(chat_id):
            logger.debug("[SESSION] No pending entry chat=%s", chat_id)
            return False

        wait = await self._registry.get(chat_id)
        if wait is None:
            logger.debug("[SESSION] Marker without registry wait chat=%s", chat_id)
            await self._storage.pop(chat_id)
            return False

        if not await self._check_filter(wait.filter, message):
            filter_name = wait.filter.__class__.__name__ if wait.filter else str(None)
            logger.debug(
                "[SESSION] Filter rejected message chat=%s, filter=%s",
                chat_id,
                filter_name,
            )
            return False

        if wait.future.done():
            logger.debug("[SESSION] Future already done chat=%s", chat_id)
            return False

        wait.future.set_result(message)
        logger.debug(
            "[SESSION] Future resolved chat=%s, message_id=%s",
            chat_id,
            message.message_id,
        )
        return True

    @staticmethod
    def _create_future() -> asyncio.Future[Message]:
        loop = asyncio.get_running_loop()
        return loop.create_future()

    @staticmethod
    async def _await_future(
        future: asyncio.Future[Message], timeout: Union[int, float]
    ) -> Message:
        return await asyncio.wait_for(future, timeout=timeout)

    @staticmethod
    async def _check_filter(filter: FilterObjectType, message: Message) -> bool:
        if filter is None:
            return True
        return await filter.call(message)

    async def _register_pending(
        self,
        chat_id: int,
        wait_id: str,
        filter: FilterObjectType,
        future: asyncio.Future[Message],
    ) -> None:
        previous = await self._registry.set(
            chat_id,
            PendingWait(wait_id=wait_id, future=future, filter=filter),
        )
        if previous is not None:
            logger.debug("[SESSION] Overwriting existing pending entry chat=%s", chat_id)
            self._registry.cancel_wait(previous, chat_id=chat_id)
        await self._storage.set(
            chat_id, WaitRecord(wait_id=wait_id, created_at=time.time())
        )

    async def _cleanup(self, chat_id: int, wait_id: str) -> None:
        wait = await self._registry.pop_if(chat_id, wait_id)
        await self._storage.pop_if(chat_id, wait_id)
        if wait is None:
            logger.debug(
                "[SESSION] Cleanup skipped stale wait chat=%s wait_id=%s",
                chat_id,
                wait_id,
            )
            return
        self._registry.cancel_wait(wait, chat_id=chat_id)
