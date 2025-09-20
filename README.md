# aiogram-input

**aiogram-input** is a lightweight and flexible library for [aiogram](https://github.com/aiogram/aiogram)  
that simplifies waiting for user responses **without FSMs**.

With `aiogram-input`, you can easily implement interactive flows where your bot waits for a specific user's
reply in a specific chat, with full support for multiple bot instances (multi-client) to avoid conflicts.

---

## ✨ Key Features

- **Simple API** – Replace FSM with a single `input()` call.
- **Filters** – Use `filter=` to capture only the messages you want.
- **Timeout Handling** – Gracefully handle unresponsive users.
- **Multi-Client** – Each bot instance has its own isolated state.
- **Race Condition Safe** – Built for concurrency.
- **Logging Integration** – Debug and monitor with ease.

---

## 📦 Installation

From PyPI:

```bash
pip install aiogram-input
```

From GitHub (latest):

```bash
pip install git+https://github.com/mamahoos/aiogram-input.git
```

---

## 💡 Usage Examples

Below are real scenarios where `aiogram-input` shines.

---

### 1. ✅ Confirm Before Action

Ask users to confirm actions before executing them.

```python
from aiogram         import Bot, Dispatcher, Router, F
from aiogram.types   import Message
from aiogram.filters import Command
from aiogram.enums   import ChatType
from aiogram_input   import InputManager

TOKEN = "YOUR_BOT_TOKEN"

bot   = Bot(TOKEN)
dp    = Dispatcher()
asker = InputManager()
dp.include_router(asker.router)

router = Router(name="confirm")

@router.message(Command("delete"), F.chat.type == ChatType.PRIVATE)
async def delete_command(message: Message):
    await message.answer("⚠️ Are you sure you want to delete your data? (yes/no)")

    response = await asker.input(message.chat.id, timeout=20)

    if response is None:
        return await message.answer("⏳ Timeout. Action canceled.")

    text = (response.text or "").lower().strip()
    if text in {"yes", "y"}:
        # Perform deletion here
        await message.answer("✅ Your data has been deleted.")
    else:
        await message.answer("❌ Action canceled.")

dp.include_router(router)
```

---

### 2. 👥 Per-User Flow Inside a Group

Capture responses only from the command initiator in busy group chats.

```python
from aiogram         import Bot, Dispatcher, Router, F
from aiogram.types   import Message
from aiogram.enums   import ChatType
from aiogram.filters import Command
from aiogram_input   import InputManager

TOKEN = "YOUR_BOT_TOKEN"

bot   = Bot(TOKEN)
dp    = Dispatcher()
asker = InputManager()
dp.include_router(asker.router)

router = Router(name="group")

@router.message(Command("register"), F.chat.type == ChatType.PRIVATE)
async def group_registration(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    await message.answer(f"👋 {message.from_user.first_name}, please enter your email:")

    response = await asker.input(chat_id, timeout=40)

    if response is None:
        return await message.answer(f"⏳ {message.from_user.first_name}, you ran out of time!")

    await message.answer(f"✅ Email saved: {response.text}")

dp.include_router(router)
```

---

### 3. 🔐 Admin-Only Confirmation

Restrict input handling to administrators using custom filters.

```python
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from aiogram.filters import Filter, Command
from aiogram_input import InputManager

TOKEN = "YOUR_BOT_TOKEN"
ADMIN_ID = 123456789

bot   = Bot(TOKEN)
dp    = Dispatcher()
asker = InputManager()
dp.include_router(asker.router)

router = Router(name="admin")

class AdminFilter(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user and message.from_user.id == ADMIN_ID

@router.message(AdminFilter(), Command("admin"))
async def secure_command(message: Message):
    await message.answer("🔐 Admin check passed! Please confirm action:")

    response = await asker.input(
        message.chat.id,
        timeout=20,
        filter=AdminFilter()
    )

    if not response:
        return await message.answer("⏳ No confirmation received.")

    text = response.text
    if text.strip().lower() in {'y', 'yes'}:
        await message.answer(f"✅ Action confirmed")
    else:
        await message.answer("❌ Action canceled.")
        

dp.include_router(router)
```

---

### 4. 📊 Multi-Step Data Collection (Form)

Build forms or registration flows without FSMs.

```python
from aiogram         import Bot, Dispatcher, Router, F
from aiogram.enums   import ChatType
from aiogram.types   import Message
from aiogram.filters import Command
from aiogram_input   import InputManager

TOKEN = "YOUR_BOT_TOKEN"

bot   = Bot(TOKEN)
dp    = Dispatcher()
asker = InputManager()
dp.include_router(asker.router)

router = Router(name="form")

@router.message(Command("form"), F.chat.type == ChatType.PRIVATE)
async def form_command(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    await message.answer("👤 What is your name?")
    name = await asker.input(chat_id, timeout=30)
    if not name:
        return await message.answer("⏳ Timeout on name.")

    await message.answer("📧 What is your email?")
    email = await asker.input(chat_id, timeout=30)
    if not email:
        return await message.answer("⏳ Timeout on email.")

    await message.answer(f"✅ Registration complete!
Name: {name.text}
Email: {email.text}")

dp.include_router(router)
```

---

### 5. ⏳ Timeout with Fallback Action

Provide fallback behavior when the user doesn’t respond in time.

```python
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram_input import InputManager

TOKEN = "YOUR_BOT_TOKEN"

bot   = Bot(TOKEN)
dp    = Dispatcher()
asker = InputManager()
dp.include_router(asker.router)

router = Router(name="timeout")

@router.message(Command("quiz"))
async def quiz_command(message: Message):
    await message.answer("❓ What is 2 + 2?")

    response = await asker.input(
        message.chat.id,
        timeout=15,
        filter=(F.from_user.id == message.from_user.id)
    )

    if response is None:
        return await message.answer("⏳ Time’s up! The correct answer is 4.")

    if response.text.strip() == "4":
        await message.answer("🎉 Correct!")
    else:
        await message.answer("❌ Wrong. The correct answer is 4.")

dp.include_router(router)
```

---

## 📖 Summary

- Use `asker.input(chat_id, timeout, filter=...)` to capture user input seamlessly.  
- Combine with filters for **per-user targeting**.
- Production-ready: async, safe, and minimal boilerplate.