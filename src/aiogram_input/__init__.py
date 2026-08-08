from importlib.metadata import PackageNotFoundError, version

from .setup import setup_input
from .storage import InputStorage, MemoryInputStorage
from .waiter import InputWaiter

try:
    __version__ = version("aiogram-input")
except PackageNotFoundError:  # pragma: no cover - only when package metadata is missing
    __version__ = "0.0.0"

__all__ = (
    "InputStorage",
    "InputWaiter",
    "MemoryInputStorage",
    "setup_input",
    "__version__",
)
