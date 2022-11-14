from __future__ import annotations

from asyncio import Lock, Semaphore
from contextlib import AbstractAsyncContextManager
from types import TracebackType
from typing import (
    AsyncContextManager,
    Awaitable,
    Callable,
    Optional,
    ParamSpec,
    Type,
    TypeVar,
)

_V = TypeVar("_V")


class AbstractAsyncLocked(AbstractAsyncContextManager[_V]):
    def __init__(self, val: _V, *, lock: AsyncContextManager[None]) -> None:
        self._val = val
        self._lock = lock

    async def replace(self, val: _V) -> _V:
        async with self._lock:
            last, self._val = self._val, val
        return last

    async def update(self, fn: Callable[[_V], Awaitable[_V]]) -> _V:
        async with self._lock:
            last, self._val = self._val, await fn(self._val)
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


class Locked(AbstractAsyncLocked[_V]):
    def __init__(self, val: _V, *, lock: Optional[Lock] = None):
        super().__init__(val, lock=lock if lock else Lock())


class Semaphored(AbstractAsyncLocked[_V]):
    def __init__(self, val: _V, *, semaphore: Optional[Semaphore] = None):
        super().__init__(val, lock=semaphore if semaphore else Semaphore())


_P = ParamSpec("_P")
_R = TypeVar("_R")


async def locked(
    f: Callable[_P, _R], *, lock: Optional[Lock] = None
) -> Callable[_P, Awaitable[_R]]:
    locked_f = Locked(f, lock=lock)

    async def inner(*args: _P.args, **kwargs: _P.kwargs) -> _R:
        async with locked_f as unlocked_f:
            res = unlocked_f(*args, **kwargs)
        return res

    return inner


async def semaphored(
    f: Callable[_P, _R], *, semaphore: Optional[Semaphore] = None
) -> Callable[_P, Awaitable[_R]]:
    locked_f = Semaphored(f, semaphore=semaphore)

    async def inner(*args: _P.args, **kwargs: _P.kwargs) -> _R:
        async with locked_f as unlocked_f:
            res = unlocked_f(*args, **kwargs)
        return res

    return inner


__all__ = [
    AbstractAsyncLocked.__name__,
    Locked.__name__,
    Semaphored.__name__,
    locked.__name__,
    semaphored.__name__,
]
