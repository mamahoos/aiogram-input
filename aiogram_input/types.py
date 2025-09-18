from typing import Any, Callable, NamedTuple, Optional
from aiogram.types import Message
from asyncio import Future

    
# Type alias for filter callback
CallbackType = Callable[..., Any]

# Pending entry structure
class PendingEntry(NamedTuple):
    filter: Optional[CallbackType]
    future: Future[Message]
    