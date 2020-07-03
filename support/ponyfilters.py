from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.handler import ctx_data

from support import ponytypes
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


class PodGameFilter(BoundFilter):
    """
    Фильтр форварда из игры
    """

    key = 'is_pod'

    def __init__(self, is_pod: bool):
        if is_pod is False:
            raise ValueError("is_pod cannot be False")

    async def check(self, message: types.Message):
        pod = 945628500
        if bool(getattr(message, "forward_date")):
            if message.forward_from.id == pod:
                return True
        return False

class LeaderFilter(BoundFilter):
    """
    Фильтр только для лидеров кланов
    """

    key = 'is_leader'

    def __init__(self, is_leader: bool):
        if is_leader is False:
            raise ValueError("is_leader cannot be False")

    async def check(self, message: types.Message):
        data = ctx_data.get()
        User: ponytypes.UserType = data["User"]
        if User.profile.leader:
            return True
        return False

class AdminFilter(BoundFilter):
    """
    Фильтр только для глобальных админов
    """

    key = 'is_botadmin'

    def __init__(self, is_botadmin: bool):
        if is_botadmin is False:
            raise ValueError("is_botadmin cannot be False")

    async def check(self, message: types.Message):
        data = ctx_data.get()
        User: ponytypes.UserType = data["User"]
        if User.profile.admin:
            return True
        return False