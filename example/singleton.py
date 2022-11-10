from __future__ import annotations
from typing import Optional

from pylocked.lock_threading import locked


class Singleton:
    _instance: Optional[Singleton] = None

    def __init__(self) -> None:
        ...

    @staticmethod
    @locked
    def get_instance() -> Singleton:
        if Singleton._instance is None:
            Singleton._instance = Singleton()
        return Singleton._instance


if __name__ == "__main__":
    Singleton.get_instance()
