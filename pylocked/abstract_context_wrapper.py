from __future__ import annotations

from contextlib import AbstractContextManager
from typing import ContextManager, TypeVar, Callable, Optional, Type
from types import TracebackType
from abc import abstractmethod

_V = TypeVar("_V")


class AbstractContextWrapper(AbstractContextManager[_V]):
    @abstractmethod
    def __init__(self, val: _V, *, context_manager: ContextManager[bool]) -> None:
        self._val = val
        self._context_manager = context_manager

    def replace(self, val: _V) -> _V:
        with self._context_manager:
            last, self._val = self._val, val
        return last

    def update(self, fn: Callable[[_V], _V]) -> _V:
        with self._context_manager:
            last, self._val = self._val, fn(self._val)
        return last

    def __enter__(self) -> _V:
        self._context_manager.__enter__()
        return self._val

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self._context_manager.__exit__(exc_type, exc_val, exc_tb)
