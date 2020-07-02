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
            user.updatedb(bothelper.db_users)

        if user.ban:
            raise CancelHandler()

        data["User"] = user

        chat = None
        if message.chat.type != "private":
            chat = await bothelper.db_chats.find_one({"_id": message.chat.id})
            if not chat:
                chat = await self.CreateNewChat(message)
            else:
                chat = ponytypes.ChatType(chat)
                chat.updatedb(bothelper.db_chats)
        data["Chat"] = chat


    async def CreateNewUser(self, update) -> ponytypes.UserType:
        """
        Создание документа для пользователя
        """
        utype = ponytypes.clear_user_type.copy()
        user: types.User = update.from_user
        User = ponytypes.UserType(utype)
        User._id = user.id
        User.name = user.full_name
        User.updatedb(bothelper.db_users)
        await User.save()
        return User

    async def CreateNewChat(self, update) -> ponytypes.ChatType:
        """
        Создание документа для чата
        """

        ctype = ponytypes.clear_chat_type.copy()
        
        if isinstance(update, types.Message):
            update: types.Message
            chat = update.chat
        else:
            update: types.CallbackQuery
            chat = update.message.chat


        Chat = ponytypes.UserType(ctype)
        Chat._id = chat.id
        Chat.updatedb(bothelper.db_chats)
        await Chat.save()
        return Chat
