from __future__ import annotations

from unittest.mock import MagicMock

from aiogram.types import Message


def make_message(chat_id: int, message_id: int = 1, text: str = "hi") -> Message:
    msg = MagicMock(spec=Message)
    msg.chat = MagicMock()
    msg.chat.id = chat_id
    msg.message_id = message_id
    msg.text = text
    return msg
