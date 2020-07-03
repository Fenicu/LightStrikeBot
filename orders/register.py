from aiogram import types
from support import ponytypes
from loguru import logger


async def NewChat(message: types.Message, User: ponytypes.UserType, Chat: ponytypes.ChatType):
    if not User.profile.leader:
        await message.answer("Вы не можете меня добавить")
        await message.chat.leave()
        return

    Chat.order = User.profile.order
    await Chat.save()
    out = f"Чату присвоен орден: {Chat.order}"
    await message.answer(out)
