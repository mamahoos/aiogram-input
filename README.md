# aiogram_input

A lightweight and flexible library for aiogram to simplify waiting for
user responses in Telegram bots. With `aiogram_input`, you can easily
implement interactive flows where your bot waits for a specific user's
reply in a specific chat, with full support for multiple bot instances
(multi-client) to avoid conflicts.

## Key Features

-   **Simple API**: Use the `input` method to wait for user messages in
    a clean and intuitive way.
-   **Multi-Client Support**: Each bot instance has its own isolated
    state, ensuring no conflicts when running multiple bots.
-   **Timeout Handling**: Built-in timeout support to gracefully handle
    unresponsive users.
-   **Custom Storage**: Provides `BaseStorage` class for extending and
    managing persistence.

## Installation

Run the following in the package directory:

``` bash
pip install .
```

Or install from GitHub:

``` bash
pip install git+https://github.com/mamahoos/aiogram-input.git
```

## Usage Example: Simple Registration with Email Validation

``` python
import re
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message
from aiogram_input import InputManager
from aiogram.enums import ChatType

TOKEN = "YOUR_BOT_TOKEN"

bot   = Bot(TOKEN)
dp    = Dispatcher()
asker = InputManager()
dp.include_router(asker.router)

email_validator = re.compile(r"^[\w.-]+@[\w.-]+\.\w+$")

router = Router(name="main")

@router.message(F.chat.type == ChatType.PRIVATE)
async def start_registration(message: Message):
    await message.answer("Welcome! Please enter your email:")
    
    response = await asker.input(message.chat.id, timeout=30)
    if response is None:
        return await message.answer("⏳ Timeout! Try again.")
    
    email = response.text
    if email is None or not email_validator.match(email):
        return await message.answer("❌ Invalid email format.")
    
    await message.answer(f"✅ Email registered: {email}")
    # Code
    ...

dp.include_router(router)

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
```

## Usage Example: Filtered Message from Admin in a Group

``` python
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from aiogram.filters import Filter, Command
from aiogram_input import InputManager

TOKEN = "YOUR_BOT_TOKEN"
ADMIN_ID = 123456789  # Replace with your admin's Telegram ID

bot   = Bot(TOKEN)
dp    = Dispatcher()
asker = InputManager()
dp.include_router(asker.router)

router = Router(name="admin")

class AdminFilter(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user and message.from_user.id == ADMIN_ID

@router.message(AdminFilter(), Command('admin'))
async def admin_handler(message: Message):
    await message.answer("👑 Admin command detected!")
    response = await asker.input(message.chat.id, timeout=20, filter=AdminFilter())
    if response:
        await message.answer(f"Admin replied: {response.text}")
        # Code
        ...
    ...

dp.include_router(router)

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
```
