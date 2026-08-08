from __future__ import annotations

from asyncio import Future
from dataclasses import dataclass
from typing import Any, Callable, Optional, Union

from aiogram import Dispatcher, Router
from aiogram.dispatcher.event.handler import FilterObject
from aiogram.types import Message

FilterObjectType = Optional[FilterObject]
CallbackType = Callable[..., Any]
Target = Union[Router, Dispatcher]


@dataclass(slots=True)
class WaitRecord:
    """Redis-safe wait marker persisted in InputStorage."""

    wait_id: str
    created_at: float


@dataclass(slots=True)
class PendingWait:
    """In-process wait state (futures and filters stay local)."""

    wait_id: str
    future: Future[Message]
    filter: FilterObjectType
