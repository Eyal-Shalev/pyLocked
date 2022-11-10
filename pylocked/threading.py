from __future__ import annotations

from abc import abstractmethod
from threading import Lock, RLock
from typing import TypeVar, Generic, Optional, runtime_checkable, Protocol, Type
from types import TracebackType

from pylocked.abstract_context_wrapper import AbstractContextWrapper

_V = TypeVar("_V")


class Locked(Generic[_V], AbstractContextWrapper[_V]):
    def __init__(self, val: _V, *, lock: Optional[Lock] = None):
        super().__init__(val, context_manager=lock if lock else Lock())


class RLocked(Generic[_V], AbstractContextWrapper[_V]):
    def __init__(self, val: _V, *, lock: Optional[RLock] = None):
        super().__init__(val, context_manager=lock if lock else RLock())
