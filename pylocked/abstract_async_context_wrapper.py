from __future__ import annotations


from contextlib import AbstractAsyncContextManager
from types import TracebackType
from typing import Callable, Optional, Type, TypeVar, AsyncContextManager, Coroutine

_V = TypeVar("_V")


class AbstractAsyncContextWrapper(AbstractAsyncContextManager[_V]):
    def __init__(self, val: _V, *, context_manager: AsyncContextManager[None]) -> None:
        self._val = val
        self._context_manager = context_manager

    async def replace(self, val: _V) -> _V:
        async with self._context_manager:
            last, self._val = self._val, val
        return last

    async def update(self, fn: Callable[[_V], Coroutine[None, None, _V]]) -> _V:
        async with self._context_manager:
            last, self._val = self._val, await fn(self._val)
        return last

    async def __aenter__(self) -> _V:
        await self._context_manager.__aenter__()
        return self._val

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self._context_manager.__aexit__(exc_type, exc_val, exc_tb)
