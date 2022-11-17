from __future__ import annotations

from abc import abstractmethod
from contextlib import AbstractContextManager
from threading import Lock, RLock
from types import TracebackType
from typing import (
    Any,
    Callable,
    ContextManager,
    Generic,
    Optional,
    ParamSpec,
    Type,
    TypeVar,
)

_V = TypeVar("_V")
_L = TypeVar("_L", bound=ContextManager[Any])


class AbstractLocked(AbstractContextManager[_V], Generic[_V, _L]):
    @abstractmethod
    def __init__(self, val: _V, *, lock: ContextManager[bool]) -> None:
        self._val = val
        self._lock = lock

    def replace(self, val: _V) -> _V:
        with self._lock:
            last, self._val = self._val, val
        return last

    def update(self, fn: Callable[[_V], _V]) -> _V:
        with self._lock:
            last, self._val = self._val, fn(self._val)
        return last

    def __enter__(self) -> _V:
        self._lock.__enter__()
        return self._val

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self._lock.__exit__(exc_type, exc_val, exc_tb)


class Locked(AbstractLocked[_V, Lock]):
    def __init__(self, val: _V, *, lock: Optional[Lock] = None):
        super().__init__(val, lock=lock if lock else Lock())


class RLocked(AbstractLocked[_V, RLock]):
    def __init__(self, val: _V, *, lock: Optional[RLock] = None):
        super().__init__(val, lock=lock if lock else RLock())


_P = ParamSpec("_P")
_R = TypeVar("_R")


def locked(f: Callable[_P, _R], *, lock: Optional[Lock] = None) -> Callable[_P, _R]:
    locked_f = Locked(f, lock=lock)

    def inner(*args: _P.args, **kwargs: _P.kwargs) -> _R:
        with locked_f as unlocked_f:
            res = unlocked_f(*args, **kwargs)
        return res

    return inner


def rlocked(f: Callable[_P, _R], *, lock: Optional[RLock] = None) -> Callable[_P, _R]:
    locked_f = RLocked(f, lock=lock)

    def inner(*args: _P.args, **kwargs: _P.kwargs) -> _R:
        with locked_f as unlocked_f:
            res = unlocked_f(*args, **kwargs)
        return res

    return inner


__all__ = [
    AbstractLocked.__name__,
    Locked.__name__,
    RLocked.__name__,
    locked.__name__,
    rlocked.__name__,
]
