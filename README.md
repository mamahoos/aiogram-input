# aiogram-input

[![PyPI](https://img.shields.io/pypi/v/aiogram-input.svg)](https://pypi.org/project/aiogram-input/)
[![Test](https://github.com/mamahoos/aiogram-input/actions/workflows/test.yml/badge.svg)](https://github.com/mamahoos/aiogram-input/actions/workflows/test.yml)
[![Redis](https://github.com/mamahoos/aiogram-input/actions/workflows/redis-integration.yml/badge.svg)](https://github.com/mamahoos/aiogram-input/actions/workflows/redis-integration.yml)

Wait for the next Telegram message inside an aiogram handler — without an FSM for every short prompt.

## Why

You ask for a phone number, a confirmation, or a one-time code. A full FSM for that is noise. You want:

```text
send question → await reply → continue
```

Register once on the Dispatcher. Await `input.wait(...)`. Get a `Message`, or `None` on timeout. FSM and other handlers still get unrelated updates.

## Install

```bash
pip install aiogram-input
```

Python 3.10+, aiogram 3.

## Setup

**Memory** (local / single process):

```python
from aiogram import Dispatcher
from aiogram_input import MemoryInputStorage, setup_input

dp = Dispatcher()
setup_input(dp, storage=MemoryInputStorage())
```

**Redis** (markers shared; use TTL so abandoned waits expire):

```python
from aiogram import Dispatcher
from aiogram_input import RedisInputStorage, setup_input
from redis.asyncio import Redis

dp = Dispatcher()
redis = Redis.from_url("redis://localhost:6379/0")
setup_input(dp, storage=RedisInputStorage(redis, ttl=300))
```

`InputWaiter` is injected into handlers (DI, like `FSMContext`).  
If `input` already means something else: `setup_input(dp, data_key="aiogram_input")`.

Redis stores wait **markers** only. The awaiting coroutine still lives on the worker that called `wait()`. Prefer `ttl=` in production.

## Examples

### DI — one setup, every router

**Pain:** waiter constructed on `dp`, again on `admin_router`, again in another file. State splits.

```python
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_input import InputWaiter

admin = Router()
support = Router()

@admin.message(Command("ban"))
async def ban_user(message: Message, input: InputWaiter):
    await message.answer("Send the user id to ban:")
    reply = await input.wait(message.chat.id, timeout=60)
    if reply is None:
        return await message.answer("Timed out.")
    await message.answer(f"Banned `{reply.text}`", parse_mode="Markdown")

@support.message(Command("ticket"))
async def open_ticket(message: Message, input: InputWaiter):
    await message.answer("Describe the issue:")
    reply = await input.wait(message.chat.id, timeout=120)
    ...

dp.include_router(admin)
dp.include_router(support)
```

### Magic filters — wait for a sticker, not chat noise

**Pain:** you ask for a sticker. People spam text. In groups, someone else replies first.

```python
from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_input import InputWaiter

@dp.message(Command("sticker_id"))
async def sticker_id(message: Message, input: InputWaiter):
    await message.answer("Send a sticker — text will be ignored.")
    sticker = await input.wait(
        message.chat.id,
        timeout=45,
        filter=(
            F.sticker
            & (F.from_user.id == message.from_user.id)
        ),
    )
    if sticker is None:
        return await message.answer("Timed out.")
    await message.answer(
        f"file_id:\n`{sticker.sticker.file_id}`",
        parse_mode="Markdown",
    )
```

### Storage — Memory locally, Redis in production

**Pain:** one process is fine on your laptop; several workers need shared wait markers and expiry.

```python
# dev
setup_input(dp, storage=MemoryInputStorage())

# prod
setup_input(dp, storage=RedisInputStorage(redis, ttl=300, key_prefix="mybot:wait:"))
```

Same `input.wait(...)` API either way.

## 3.x → 4.x

`InputManager` is removed. Use `setup_input(dp)` + `input.wait(...)`.

## License

MIT
