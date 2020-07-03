from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from support.bothelper import bot


class BotAddFilter(BoundFilter):
    """
    Фильтр для проверки, что бота добавили в чат
    """

    key = 'is_addbot'

    def __init__(self, is_addbot: bool):
        if is_addbot is False:
            raise ValueError("is_addbot cannot be False")

    async def check(self, message: types.Message):
        Bot = await bot.me
        for user in message.new_chat_members:
            if user.id == Bot.id:
                return True
        return False
