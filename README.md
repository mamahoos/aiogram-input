# aiogram-input

[![PyPI](https://img.shields.io/pypi/v/aiogram-input.svg)](https://pypi.org/project/aiogram-input/)
[![Test](https://github.com/mamahoos/aiogram-input/actions/workflows/test.yml/badge.svg)](https://github.com/mamahoos/aiogram-input/actions/workflows/test.yml)

Wait for the next Telegram message inside an aiogram handler — without building an FSM for every short prompt.

## Why

Aiogram FSM is great for multi-step flows. It is heavy for “ask once, wait, continue.”

`aiogram-input` gives you that one awaitable wait: register once on the Dispatcher, call `input.wait(...)` from any handler, get a `Message` or `None` on timeout. Unrelated updates still reach FSM and other handlers.

## Install

```bash
pip install -U aiogram-input
```

Requires Python 3.10+ and aiogram 3.

## Usage

```python
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_input import InputWaiter, setup_input

dp = Dispatcher()
setup_input(dp)  # once

@dp.message(Command("name"))
async def ask_name(message: Message, input: InputWaiter):
    await message.answer("What is your name?")
    reply = await input.wait(
        message.chat.id,
        timeout=30,
        filter=F.from_user.id == message.from_user.id,
    )
    if reply is None:
        return await message.answer("Timed out.")
    await message.answer(f"Hi, {reply.text}")
```

`setup_input` injects `InputWaiter` into handlers (like `FSMContext`). Optional: `setup_input(dp, storage=MemoryInputStorage())` for a custom `InputStorage`.

## 3.x → 4.0

`InputManager` is gone. Use `setup_input(dp)` + `input.wait(...)` instead of `InputManager(router).input(...)`.

## License

MIT
