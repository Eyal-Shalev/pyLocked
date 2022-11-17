from typing import Generic, TypeVar

_V = TypeVar("_V")


class Ref(Generic[_V]):
    def __init__(self, val: _V) -> None:
        self.val = val
