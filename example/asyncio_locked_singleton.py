from __future__ import annotations

import random
from asyncio import sleep
from typing import Optional

from pylocked.asyncio import async_locked


class LockedSingleton:
    _instance: Optional[LockedSingleton] = None

    @async_locked
    @staticmethod
    async def get_instance() -> LockedSingleton:
        if LockedSingleton._instance is None:
            tmp = LockedSingleton()
            await sleep(random.uniform(0, 1))  # Long process
            LockedSingleton._instance = tmp
        return LockedSingleton._instance
