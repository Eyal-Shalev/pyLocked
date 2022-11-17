from __future__ import annotations

from asyncio import Lock, iscoroutinefunction
from contextlib import AbstractAsyncContextManager
from types import TracebackType
from typing import (
    Any,
    AsyncContextManager,
    Awaitable,
    Callable,
    Generic,
    Optional,
    ParamSpec,
    Type,
    TypeVar,
)

_V = TypeVar("_V")
_L = TypeVar("_L", bound=AsyncContextManager[Any])


class CustomAsyncLocked(AbstractAsyncContextManager[_V], Generic[_V, _L]):
    """
    Locks any reference using the provided lock.
    """

    def __init__(self, val: _V, *, lock: _L) -> None:
        self._val = val
        self._lock = lock

    async def replace(self, val: _V) -> _V:
        """
        Replaces the reference in a concurrent safe way.
        :returns: The old reference.
        """
        async with self._lock:
            last, self._val = self._val, val
        return last

    async def update(self, fn: Callable[[_V], _V | Awaitable[_V]]) -> _V:
        """
        Updates the reference using a provided callable.
        :returns: The old reference.
        """
        async with self._lock:
            if iscoroutinefunction(fn):
                ref = await fn(self._val)
            else:
                ref = fn(self._val)
            last, self._val = self._val, ref
        return last

    async def __aenter__(self) -> _V:
        await self._lock.__aenter__()
        return self._val

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self._lock.__aexit__(exc_type, exc_val, exc_tb)


class AsyncLocked(CustomAsyncLocked[_V, Lock]):
    """
    Implements :class:`pylocked.asyncio.CustomAsyncLocked` using :py:class:`asyncio.Lock`
    """

    def __init__(self, val: _V, *, lock: Optional[Lock] = None):
        """
        Initializes :class:`pylocked.asyncio.AsyncLocked`
        :param val: The reference to lock
        :param lock: If provided, :class:`pylocked.asyncio.AsyncLocked` will use it as the internal lock
        """
        super().__init__(val, lock=lock if lock else Lock())


_P = ParamSpec("_P")
_R = TypeVar("_R")


def custom_locked(
    f: Callable[_P, Awaitable[_R]], *, lock: _L
) -> Callable[_P, Awaitable[_R]]:
    locked_f = CustomAsyncLocked[Callable[_P, Awaitable[_R]], _L](f, lock=lock)
    """
    Decorator to lock functions
    """

    async def inner(*args: _P.args, **kwargs: _P.kwargs) -> _R:
        async with locked_f as unlocked_f:
            res = await unlocked_f(*args, **kwargs)
        return res

    return inner


def async_locked(
    f: Callable[_P, Awaitable[_R]], *, lock: Optional[Lock] = None
) -> Callable[_P, Awaitable[_R]]:
    return custom_locked(f, lock=lock if lock else Lock())


__all__ = [
    CustomAsyncLocked.__name__,
    AsyncLocked.__name__,
    custom_locked.__name__,
    async_locked.__name__,
]
