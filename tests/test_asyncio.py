from __future__ import annotations

import os
from asyncio import Lock, Semaphore, create_task, gather, wait_for
from functools import partial
from typing import Any, Type

import pytest
from tests.utils.ref import Ref

from pylocked.asyncio import Locked, Semaphored


@pytest.mark.asyncio
@pytest.mark.parametrize("size", [100])
@pytest.mark.parametrize(
    "lock_cls",
    [
        Locked,
        Semaphored,
        partial(Locked, lock=Lock()),
        partial(Semaphored, semaphore=Semaphore(1)),
    ],
)
async def test_with_lock(
    size: int, lock_cls: Type[Locked[Ref[int]] | Semaphored[Ref[int]]]
) -> None:
    locked_counter = lock_cls(Ref(0))

    async def inc() -> None:
        async with locked_counter as counter:
            tmp = counter.val + 1
            os.sched_yield()
            counter.val = tmp

    await gather(*[create_task(inc()) for _ in range(size)])
    assert locked_counter._val.val == size


@pytest.mark.asyncio
@pytest.mark.parametrize("size", [100])
@pytest.mark.parametrize(
    "lock_cls",
    [
        Locked,
        Semaphored,
        partial(Locked, lock=Lock()),
        partial(Semaphored, semaphore=Semaphore(1)),
    ],
)
async def test_update(size: int, lock_cls: Type[Locked[int] | Semaphored[int]]) -> None:
    locked_counter = lock_cls(0)

    async def do_inc(val: int) -> int:
        return val + 1

    async def inc(*_: Any) -> None:
        await locked_counter.update(do_inc)

    await gather(*[create_task(inc()) for _ in range(size)])
    assert locked_counter._val == size


@pytest.mark.asyncio
@pytest.mark.parametrize("size", [100])
@pytest.mark.parametrize(
    "lock_cls",
    [
        Locked,
        Semaphored,
        partial(Locked, lock=Lock()),
        partial(Semaphored, semaphore=Semaphore(1)),
    ],
)
async def test_replace(lock_cls: Type[Locked[int] | Semaphored[int]]) -> None:
    locked_counter = lock_cls(0)
    await locked_counter.__aenter__()

    async def replace() -> None:
        await locked_counter.replace(5)

    co = replace()

    assert locked_counter._val == 0
    await locked_counter.__aexit__(None, None, None)

    await wait_for(co, timeout=1)
    assert locked_counter._val == 5
