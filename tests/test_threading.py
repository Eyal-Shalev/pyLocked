from __future__ import annotations

import os
import threading
from concurrent.futures import FIRST_EXCEPTION, ThreadPoolExecutor, wait
from functools import partial
from threading import Lock, RLock
from typing import Callable, Type

import pytest
from tests.utils.ref import Ref

from pylocked.threading import Locked, RLocked, locked, rlocked


@pytest.mark.parametrize("size", [100])
@pytest.mark.parametrize("lock_dec", [locked, rlocked])
def test_decorator(
    size: int, lock_dec: Callable[[Callable[[], None]], Callable[[], None]]
) -> None:
    counter = 0

    @lock_dec
    def foo() -> None:
        nonlocal counter
        tmp = counter + 1
        os.sched_yield()
        counter = tmp

    pool = ThreadPoolExecutor()

    wait(
        [pool.submit(foo) for _ in range(size)], timeout=10, return_when=FIRST_EXCEPTION
    )
    assert counter == size
    pool.shutdown(wait=False, cancel_futures=True)


@pytest.mark.parametrize("size", [100])
@pytest.mark.parametrize(
    "lock_cls",
    [
        Locked,
        RLocked,
        partial(Locked, lock=Lock()),
        partial(RLocked, lock=RLock()),
    ],
)
def test_with_lock(
    size: int, lock_cls: Type[Locked[Ref[int]] | RLocked[Ref[int]]]
) -> None:
    locked_counter = lock_cls(Ref(0))
    pool = ThreadPoolExecutor()

    def inc() -> None:
        with locked_counter as counter:
            tmp = counter.val + 1
            os.sched_yield()
            counter.val = tmp

    wait(
        [pool.submit(inc) for _ in range(size)], timeout=1, return_when=FIRST_EXCEPTION
    )
    assert locked_counter._val.val == size
    pool.shutdown(wait=False, cancel_futures=True)


@pytest.mark.parametrize("size", [100])
@pytest.mark.parametrize(
    "lock_cls",
    [
        Locked,
        RLocked,
        partial(Locked, lock=Lock()),
        partial(RLocked, lock=RLock()),
    ],
)
def test_update(size: int, lock_cls: Type[Locked[int] | RLocked[int]]) -> None:
    locked_counter = lock_cls(0)
    pool = ThreadPoolExecutor()

    def inc() -> None:
        locked_counter.update(lambda val: val + 1)

    wait(
        [pool.submit(inc) for _ in range(size)], timeout=1, return_when=FIRST_EXCEPTION
    )
    assert locked_counter._val == size
    pool.shutdown(wait=False, cancel_futures=True)


@pytest.mark.parametrize(
    "lock_cls",
    [
        Locked,
        RLocked,
        partial(Locked, lock=Lock()),
        partial(RLocked, lock=RLock()),
    ],
)
def test_replace(lock_cls: Type[Locked[int] | RLocked[int]]) -> None:
    locked_counter = lock_cls(0)
    ev = threading.Event()

    locked_counter.__enter__()

    def replace() -> None:
        locked_counter.replace(5)
        ev.set()

    t = threading.Thread(target=replace)
    t.start()

    assert locked_counter._val == 0
    locked_counter.__exit__(None, None, None)
    assert ev.wait(timeout=1)
    assert locked_counter._val == 5
    t.join(timeout=1)
