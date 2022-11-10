from __future__ import annotations

from contextlib import AbstractContextManager
from typing import ContextManager, TypeVar, Callable, Optional, Type
from types import TracebackType
from abc import abstractmethod

_V = TypeVar("_V")


class AbstractContextWrapper(AbstractContextManager[_V]):
    @abstractmethod
    def __init__(self, val: _V, *, wrapper: ContextManager[bool]) -> None:
        self._val = val
        self._wrapper = wrapper

    def replace(self, val: _V) -> _V:
        with self._wrapper:
            last, self._val = self._val, val
        return last

    def update(self, fn: Callable[[_V], _V]) -> _V:
        with self._wrapper:
            last, self._val = self._val, fn(self._val)
        return last

    def __enter__(self) -> _V:
        self._wrapper.__enter__()
        return self._val

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self._wrapper.__exit__(exc_type, exc_val, exc_tb)
