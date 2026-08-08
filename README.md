# aiogram-input

[![PyPI](https://img.shields.io/pypi/v/aiogram-input.svg)](https://pypi.org/project/aiogram-input/)
[![Test](https://github.com/mamahoos/aiogram-input/actions/workflows/test.yml/badge.svg)](https://github.com/mamahoos/aiogram-input/actions/workflows/test.yml)

Wait for the next Telegram message inside an aiogram handler — without an FSM for every short prompt.

## Why

You ask for a phone number, a confirmation, or a one-time code. A full FSM for that is noise. You want:

```text
send question → await reply → continue
```

Register once on the Dispatcher. Await `input.wait(...)`. Get a `Message`, or `None` on timeout. FSM and other handlers still get unrelated updates.

## Install

```bash
pip install -U aiogram-input
```

Python 3.10+, aiogram 3.

## Setup

```python
from aiogram import Dispatcher
from aiogram_input import MemoryInputStorage, setup_input

dp = Dispatcher()

# Local / single process
setup_input(dp, storage=MemoryInputStorage())

# Production (multi-worker): same API, Redis-backed storage
# setup_input(dp, storage=RedisInputStorage(redis))

# If `input` already means something else in your handlers:
# setup_input(dp, data_key="aiogram_input")
```

`InputWaiter` is injected into handlers (DI, like `FSMContext`). Storage is swappable via `InputStorage` (**Memory** today, **Redis** when you scale). The DI key is configurable (`data_key`, default `"input"`).

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

**Pain:** you ask for a sticker pack preview. People spam text. In groups, someone else replies first.

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

Only a sticker from the same user resolves the wait. Texts, photos, and other users’ stickers keep flowing to the rest of your bot.

## 3.x → 4.x

`InputManager` is removed. Use `setup_input(dp)` + `input.wait(...)`.

## License

MIT
