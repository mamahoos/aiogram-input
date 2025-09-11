from abc             import ABC, abstractmethod
from aiogram.filters import Filter
from typing          import Optional, Tuple
from asyncio         import Future
from aiogram.types   import Message

class BaseStorage(ABC):
    @abstractmethod
    def set(self, chat_id: int, /, filter: Optional[Filter], future: Future[Message]) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def pop(self, chat_id: int, /) -> Future[Message]:
        raise NotImplementedError
    
    @abstractmethod
    def get(self, chat_id: int, /) -> Optional[Tuple[Filter, Future[Message]]]:
        raise NotImplementedError
    
    def __contains__(self, chat_id: int, /) -> bool:
        return self.get(chat_id) is not None