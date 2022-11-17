pylocked provides utility classes (and functions) to lock any resource (or function) and thus make them thread and / or concurrency safe.

## Install

From pip:

```shell
pip install pylocked
```

From repository:

```shell
pip install git+https://github.com/Eyal-Shalev/pylocked
```

## Examples

### AsyncIO

#### `pylocked.asyncio.AsyncLocked`

```python
from pylocked.asyncio import AsyncLocked

locked_arr: Locked[list[int]] = Locked([])

async def double():
  async with locked_arr as arr:
    for i in range(len(arr)):
      arr[i] += arr[i]

async def reset():
  await locked_arr.replace(list(range(10)))

async def duplicate():
  await locked_arr.update(lambda arr: arr * 2)
```

#### `pylocked.asyncio.async_locked()`

```python
from typing import Optional

from pylocked.asyncio import locked

class LockedSingleton:
    _instance: Optional[LockedSingleton] = None

    @locked
    @staticmethod
    async def get_instance() -> LockedSingleton:
        if LockedSingleton._instance is None:
            LockedSingleton._instance = LockedSingleton()
        return LockedSingleton._instance
```

### Threading

#### `pylocked.threading.RLocked`
> You can use `pylocked.threading.Locked` if you want to use `threading.Lock` instead.

```python
from pylocked.threading import RLocked

locked_arr: RLocked[list[int]] = RLocked([])

def double():
  with locked_arr as arr:
    for i in range(len(arr)):
      arr[i] += arr[i]

def reset():
  locked_arr.replace(list(range(10)))

def duplicate():
  locked_arr.update(lambda arr: arr * 2)
```

#### `pylocked.threading.rlocked()`
> You can use `pylocked.threading.locked()` if you want to use `threading.Lock` instead.

```python
from typing import Optional

from pylocked.threading import rlocked

class LockedSingleton:
    _instance: Optional[LockedSingleton] = None

    @rlocked
    @staticmethod
    def get_instance() -> LockedSingleton:
        if LockedSingleton._instance is None:
            LockedSingleton._instance = LockedSingleton()
        return LockedSingleton._instance
```
