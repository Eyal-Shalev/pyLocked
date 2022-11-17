from __future__ import annotations

import random
import time
from typing import Optional

from pylocked.threading import rlocked


class LockedSingleton:
    _instance: Optional[LockedSingleton] = None

    @rlocked
    @staticmethod
    def get_instance() -> LockedSingleton:
        if LockedSingleton._instance is None:
            tmp = LockedSingleton()
            time.sleep(random.uniform(0, 1))  # Long process
            LockedSingleton._instance = tmp
        return LockedSingleton._instance
