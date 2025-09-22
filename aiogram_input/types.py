from typing        import Any, Callable, NamedTuple, Optional, Union
from aiogram.types import Message
from asyncio       import Future
from aiogram       import Dispatcher, Router
from aiogram.dispatcher.event.handler import FilterObject

# Type alias for filter object
FilterObjectType = Optional[FilterObject]

# Type alias for filter callback
CallbackType     = Callable[..., Any]

# Type alias for Router or Dispatcher
Target           = Union[Router, Dispatcher]

# Pending entry structure
class PendingEntry(NamedTuple):
    filter: FilterObjectType
    future: Future[Message]
    