from __future__ import annotations

import json
import logging
from typing import Any, Optional

from ..types import WaitRecord

logger = logging.getLogger(__name__)

_POP_IF_SCRIPT = """
local raw = redis.call('GET', KEYS[1])
if not raw then
  return nil
end
local data = cjson.decode(raw)
if data['wait_id'] ~= ARGV[1] then
  return nil
end
redis.call('DEL', KEYS[1])
return raw
"""


class RedisInputStorage:
    """
    Redis-backed InputStorage for wait markers.

    Futures/filters stay in-process on the worker that called ``wait()``.
    Redis only stores markers so TTLs and cross-process visibility of "someone
    is waiting" work; resolving still requires the owning process (or a future
    pub/sub bridge). Use ``ttl`` so abandoned markers cannot grow forever.

    Requires: ``pip install aiogram-input[redis]``.
    """

    def __init__(
        self,
        redis: Any,
        /,
        *,
        key_prefix: str = "aiogram_input:wait:",
        ttl: Optional[int] = None,
    ) -> None:
        if not isinstance(key_prefix, str) or not key_prefix:
            raise ValueError("key_prefix must be a non-empty string")
        if ttl is not None and ttl <= 0:
            raise ValueError("ttl must be a positive integer or None")
        self._redis = redis
        self._prefix = key_prefix
        self._ttl = ttl
        self._pop_if = redis.register_script(_POP_IF_SCRIPT)

    def _key(self, chat_id: int) -> str:
        return f"{self._prefix}{chat_id}"

    @staticmethod
    def _dumps(record: WaitRecord) -> str:
        return json.dumps(
            {"wait_id": record.wait_id, "created_at": record.created_at},
            separators=(",", ":"),
        )

    @classmethod
    def _loads(cls, raw: Any) -> Optional[WaitRecord]:
        try:
            if isinstance(raw, bytes):
                raw = raw.decode()
            data = json.loads(raw)
            wait_id = data["wait_id"]
            created_at = float(data["created_at"])
            if not isinstance(wait_id, str) or not wait_id:
                raise ValueError("invalid wait_id")
            return WaitRecord(wait_id=wait_id, created_at=created_at)
        except (TypeError, ValueError, KeyError, json.JSONDecodeError, UnicodeError):
            logger.warning("[REDIS] Ignoring corrupt wait marker payload")
            return None

    async def get(self, chat_id: int, /) -> Optional[WaitRecord]:
        raw = await self._redis.get(self._key(chat_id))
        if raw is None:
            return None
        record = self._loads(raw)
        if record is None:
            await self._redis.delete(self._key(chat_id))
        return record

    async def set(self, chat_id: int, record: WaitRecord, /) -> None:
        key = self._key(chat_id)
        payload = self._dumps(record)
        if self._ttl is None:
            await self._redis.set(key, payload)
        else:
            await self._redis.set(key, payload, ex=self._ttl)

    async def pop(self, chat_id: int, /) -> Optional[WaitRecord]:
        raw = await self._redis.getdel(self._key(chat_id))
        if raw is None:
            return None
        return self._loads(raw)

    async def pop_if(self, chat_id: int, wait_id: str, /) -> Optional[WaitRecord]:
        raw = await self._pop_if(keys=[self._key(chat_id)], args=[wait_id])
        if raw is None:
            return None
        return self._loads(raw)

    async def contains(self, chat_id: int, /) -> bool:
        return bool(await self._redis.exists(self._key(chat_id)))
