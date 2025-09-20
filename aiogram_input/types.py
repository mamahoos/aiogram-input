from typing        import Any, Callable, NamedTuple, Optional
from aiogram.types import Message
from asyncio       import Future
from aiogram.dispatcher.event.handler import FilterObject

# Type alias for filter object
FilterObjectType = Optional[FilterObject]

# Type alias for filter callback
CallbackType     = Callable[..., Any]

# Pending entry structure
class PendingEntry(NamedTuple):
    filter: FilterObjectType
    future: Future[Message]
    