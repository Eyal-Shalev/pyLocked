from asyncio import Lock, Semaphore
from typing import Generic, TypeVar, Optional

import asyncio

from pylocked.abstract_async_context_wrapper import AbstractAsyncContextWrapper


_V = TypeVar('_V')


class Locked(AbstractAsyncContextWrapper[_V]):
    def __init__(self, val: _V, *, lock: Optional[Lock] = None):
        super().__init__(val, context_manager=lock if lock else Lock())


class Semaphored(AbstractAsyncContextWrapper[_V]):
    def __init__(self, val: _V, *, semaphore: Optional[Semaphore] = None):
        super().__init__(val, context_manager=semaphore if semaphore else Semaphore())
