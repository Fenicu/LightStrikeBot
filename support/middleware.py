from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from loguru import logger

from support import bothelper, ponytypes


class UserMiddleware(BaseMiddleware):
    def __init__(self):
        super(UserMiddleware, self).__init__()


    async def on_pre_process_message(self, message: types.Message, data: dict):
        if message.from_user.id == 777000: # не обрабатываем сообщения от телеграма
            raise CancelHandler()

        user = await bothelper.db_users.find_one({"_id": message.from_user.id})
        if not user:
            user = await self.CreateNewUser(message)
        else:
            user = ponytypes.UserType(user)
        
        if user.ban:
            raise CancelHandler()






    async def CreateNewUser(self, update) -> ponytypes.UserType:
        """
        Создание документа для пользователя
        """

        user: types.User = update.from_user
        User = ponytypes.UserType(ponytypes.clear_user_type)
        User._id = user.id
        User.name = user.full_name
        User._db = bothelper.db_users
        await User.save()
        return User