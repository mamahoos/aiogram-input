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
from aiogram import Bot, Dispatcher
from aiogram_ask import Asker

# Create an Asker instance for your bot
asker = Asker()
dp = Dispatcher()
dp.include_router(asker.router)  # Add the Asker router

# Example: Collect and validate an email address
router = Router()
@router.message(filters.Command("email"))
async def collect_email(message: Message):
    await message.answer("📧 Please provide your email address:")
    response = await asker.ask(message.from_user.id, message.chat.id, timeout=30)
    if response:
        email = response.text.strip()
        if "@" in email and "." in email:
            await message.answer(f"✅ Valid email received: {email}")
        else:
            await message.answer("❌ Invalid email format. Please try again.")
    else:
        await message.answer("⏳ Timeout! Please use /email to try again.")

dp.include_router(router)
# code..
```