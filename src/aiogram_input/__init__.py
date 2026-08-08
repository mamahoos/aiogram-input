from importlib.metadata import PackageNotFoundError, version

from .core import InputManager
from .storage import InputStorage, MemoryInputStorage

try:
    __version__ = version("aiogram-input")
except PackageNotFoundError:  # pragma: no cover - only when package metadata is missing
    __version__ = "0.0.0"

__all__ = (
    "InputManager",
    "InputStorage",
    "MemoryInputStorage",
    "__version__",
)
