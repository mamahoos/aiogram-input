# aiogram-input

[![PyPI](https://img.shields.io/pypi/v/aiogram-input.svg)](https://pypi.org/project/aiogram-input/)
[![Python](https://img.shields.io/pypi/pyversions/aiogram-input.svg)](https://pypi.org/project/aiogram-input/)
[![Test](https://github.com/mamahoos/aiogram-input/actions/workflows/test.yml/badge.svg)](https://github.com/mamahoos/aiogram-input/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Await the next user message in [aiogram](https://github.com/aiogram/aiogram) bots — Dispatcher-scoped setup, handler DI, pluggable storage.

Works with aiogram FSM: only matching waits consume messages; everything else passes through.

**Current release:** [`4.0.0`](https://pypi.org/project/aiogram-input/4.0.0/) on PyPI.

## Features

- One-time `setup_input(dp)` on the Dispatcher
- `InputWaiter` injected into handlers as `input` (same idea as `FSMContext`)
- Timeouts, filters, and safe overwrite of in-flight waits
- `InputStorage` protocol + `MemoryInputStorage` (Redis-ready boundary)
- Typed package (`py.typed`)

## Requirements

- Python **3.10+**
- aiogram **3.x**

## Install

```bash
pip install -U aiogram-input
# or
uv add aiogram-input
```

```bash
pip install "aiogram-input==4.0.0"
```

## Quick start

```python
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_input import InputWaiter, MemoryInputStorage, setup_input

bot = Bot("TOKEN")
dp = Dispatcher()
setup_input(dp, storage=MemoryInputStorage())

@dp.message(Command("ask"))
async def ask(message: Message, input: InputWaiter):
    await message.answer("Send your name")
    reply = await input.wait(
        chat_id=message.chat.id,
        timeout=30,
        filter=F.from_user.id == message.from_user.id,
    )
    if reply is None:
        return await message.answer("Timed out")
    await message.answer(f"Hello, {reply.text}")
```

Call `setup_input(dp)` once. Include routers as usual — do **not** construct a waiter per router.

## Migration from 3.x → 4.0

Breaking change: `InputManager` is removed.

```python
# 3.x
from aiogram_input import InputManager
asker = InputManager(dp)  # or InputManager(router)
response = await asker.input(chat_id, timeout=20, filter=...)

# 4.0
from aiogram_input import InputWaiter, setup_input
setup_input(dp)  # once, on Dispatcher only

@dp.message(Command("ask"))
async def ask(message: Message, input: InputWaiter):
    response = await input.wait(message.chat.id, timeout=20, filter=...)
```

| 3.x | 4.0 |
| --- | --- |
| `InputManager(target)` | `setup_input(dp, storage=...)` |
| `asker.input(...)` | `input.wait(...)` |
| Setup on Router or Dispatcher | Dispatcher only |
| Built-in dict storage | `MemoryInputStorage` / custom `InputStorage` |

Upgrade:

```bash
pip install -U "aiogram-input>=4.0.0"
```

## Examples

### Confirm before action

```python
@dp.message(Command("delete"))
async def delete_command(message: Message, input: InputWaiter):
    await message.answer("Delete your data? (yes/no)")
    response = await input.wait(message.chat.id, timeout=20)
    if response is None:
        return await message.answer("Timeout. Canceled.")
    if (response.text or "").lower().strip() in {"yes", "y"}:
        await message.answer("Deleted.")
    else:
        await message.answer("Canceled.")
```

### Per-user filter in groups

```python
@dp.message(Command("register"))
async def register(message: Message, input: InputWaiter):
    await message.answer("Enter your email:")
    response = await input.wait(
        message.chat.id,
        timeout=40,
        filter=F.from_user.id == message.from_user.id,
    )
    if response is None:
        return await message.answer("Timed out.")
    await message.answer(f"Saved: {response.text}")
```

### Multi-step form

```python
@dp.message(Command("form"))
async def form(message: Message, input: InputWaiter):
    chat_id = message.chat.id
    await message.answer("Name?")
    name = await input.wait(chat_id, timeout=30)
    if not name:
        return await message.answer("Timeout on name.")
    await message.answer("Email?")
    email = await input.wait(chat_id, timeout=30)
    if not email:
        return await message.answer("Timeout on email.")
    await message.answer(f"Done\nName: {name.text}\nEmail: {email.text}")
```

## Storage

```python
from aiogram_input import MemoryInputStorage, setup_input

setup_input(dp, storage=MemoryInputStorage())
```

`InputStorage` stores only wait markers (safe to back with Redis later). Futures stay in-process in an internal registry.

## Develop

```bash
uv sync --group dev
uv run pytest
uv build
```

CI runs on every push/PR to `main` (Python 3.10–3.13). Releases publish to PyPI on `v*` tags.

## License

MIT — see [LICENSE](LICENSE).
