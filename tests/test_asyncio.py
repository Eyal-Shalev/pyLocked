from __future__ import annotations

import os
from asyncio import Lock, create_task, gather, wait_for
from functools import partial
from typing import Any, Awaitable, Callable, Type

import pytest
from tests.utils.ref import Ref

from pylocked.asyncio import AsyncLocked

# TODO: add test for async_locked


@pytest.mark.asyncio
@pytest.mark.parametrize("size", [100])
@pytest.mark.parametrize(
    "lock_cls",
    [
        AsyncLocked,
        partial(AsyncLocked, lock=Lock()),
    ],
)
async def test_with_lock(size: int, lock_cls: Type[AsyncLocked[Ref[int]]]) -> None:
    locked_counter = lock_cls(Ref(0))

    async def inc() -> None:
        async with locked_counter as counter:
            tmp = counter.val + 1
            os.sched_yield()
            counter.val = tmp

    await gather(*[create_task(inc()) for _ in range(size)])
    assert locked_counter._val.val == size


async def async_do_inc(val: int) -> int:
    return val + 1


def do_inc(val: int) -> int:
    return val + 1


@pytest.mark.asyncio
@pytest.mark.parametrize("size", [100])
@pytest.mark.parametrize("fn", [do_inc, async_do_inc])
@pytest.mark.parametrize(
    "lock_cls",
    [
        AsyncLocked,
        partial(AsyncLocked, lock=Lock()),
    ],
)
async def test_update(
    size: int,
    fn: Callable[[int], Awaitable[int] | int],
    lock_cls: Type[AsyncLocked[int]],
) -> None:
    locked_counter = lock_cls(0)

    async def inc(*_: Any) -> None:
        await locked_counter.update(fn)

    await gather(*[create_task(locked_counter.update(fn)) for _ in range(size)])
    assert locked_counter._val == size


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "lock_cls",
    [
        AsyncLocked,
        partial(AsyncLocked, lock=Lock()),
    ],
)
async def test_replace(lock_cls: Type[AsyncLocked[int]]) -> None:
    locked_counter = lock_cls(0)
    await locked_counter.__aenter__()

    async def replace() -> None:
        await locked_counter.replace(5)

    co = replace()

    assert locked_counter._val == 0
    await locked_counter.__aexit__(None, None, None)

    await wait_for(co, timeout=1)
    assert locked_counter._val == 5
