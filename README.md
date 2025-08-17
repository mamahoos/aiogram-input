# aiogram_ask

A lightweight and flexible library for aiogram to simplify waiting for user responses in Telegram bots. With `aiogram_ask`, you can easily implement interactive flows where your bot waits for a specific user's reply in a specific chat, with full support for multiple bot instances (multi-client) to avoid conflicts.

## Key Features
- **Simple API**: Use the `Asker` class to wait for user messages with a single `ask` method.
- **Multi-Client Support**: Each bot instance has its own isolated state, ensuring no conflicts when running multiple bots.
- **Timeout Handling**: Built-in timeout support to gracefully handle unresponsive users.

## Installation
Run the following in the package directory:
```
pip install .
```

Or install from GitHub:
```
pip install git+https://github.com/mamahoos/aiogram-ask.git
```

## Usage
```python
from aiogram import Bot, Dispatcher, filters, Router
from aiogram_ask import Asker

# Create an Asker instance for your bot
asker = Asker()
dp    = Dispatcher()
bot   = Bot(token=...)
dp.include_router(asker.router)  # Add the Asker router
# ----------

router = Router(name='start')

@router.message()
async def collect_message(message: Message):
    await message.answer("Say something!")
    response = await asker.ask(message.from_user.id, message.chat.id, timeout=30)
    if not response:
        await message.answer("⏳ Timeout!")
    else:
        await message.answer(f"You said {response.text}!")

dp.include_router(router)

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
```
