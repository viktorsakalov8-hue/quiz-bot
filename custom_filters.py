from pyrogram import filters
from pyrogram.types import Message, KeyboardButton


def button_filter(button: KeyboardButton):
    async def func(_, __, messasge: Message):
        return messasge.text == button.text
    return filters.create(func, "ButtonFilters", button=button)

