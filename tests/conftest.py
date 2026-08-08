from __future__ import annotations

import pytest

from aiogram_input.registry import WaitRegistry
from aiogram_input.session import SessionManager
from aiogram_input.storage import MemoryInputStorage

from .helpers import make_message

__all__ = ["make_message"]


@pytest.fixture
def storage() -> MemoryInputStorage:
    return MemoryInputStorage()


@pytest.fixture
def registry() -> WaitRegistry:
    return WaitRegistry()


@pytest.fixture
def session(storage: MemoryInputStorage, registry: WaitRegistry) -> SessionManager:
    return SessionManager(storage, registry)
