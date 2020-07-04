import re

import emoji
from aiogram import types
from aiogram.utils.markdown import hlink
from loguru import logger

from support import ponytypes


async def NewChat(message: types.Message, User: ponytypes.UserType, Chat: ponytypes.ChatType):
    from support.bothelper import db_chats
    from support.bothelper import db_orders
    if not User.profile.leader:
        await message.answer("Вы не можете меня добавить")
        await message.chat.leave()
        await db_chats.delete_one({"_id": message.chat.id})
        return

    order = await db_chats.find_one({"order": User.profile.order})
    if order:
        await message.answer("Такой ордер уже существует, ты чо, пёс")
        await message.chat.leave()
        await db_chats.delete_one({"_id": message.chat.id})
        return

    Chat.order = User.profile.order
    await Chat.save()
    out = f"Чату присвоен орден: {emoji.emojize(Chat.order)}"
    await message.answer(out)


async def RegisterNewOrder(message: types.Message):
    from support.bothelper import db_orders
    order_icon = re.search(r"(:.*:)", emoji.demojize(message.text)).group(1)
    order = await db_orders.find_one({"_id": order_icon})
    if order:
        await message.answer("Такой ордер уже существует, ты чо, пёс")
        return
    order = {"_id": order_icon}
    await db_orders.insert_one(order)
    await message.answer(f"Ордер {order_icon} был сохранён")

async def DeleteOrder(message: types.Message):
    from support.bothelper import db_orders
    order_icon = re.search(r"(:.*:)", emoji.demojize(message.text)).group(1)
    result = await db_orders.delete_one({"_id": order_icon})
    if result.deleted_count > 0:
        await message.answer(f"Ордер: {order_icon} был удалён")
        return
    await message.answer("Такого ордера нет")

async def NewLeader(message: types.Message):
    from support.bothelper import db_users
    userlink = hlink(message.reply_to_message.from_user.full_name, message.reply_to_message.from_user.url)
    User = ponytypes.UserType(await db_users.find_one({"_id": message.reply_to_message.from_user.id}))
    if User.profile.order is None:
        await message.answer(f"{userlink} не числится в ордене")
        return
    User.updatedb(db_users)
    User.profile.leader = True
    await User.save()
    await message.answer(f"{userlink} был назначен главой {emoji.emojize(User.profile.order)}")


async def RemoveLeader(message: types.Message):
    from support.bothelper import db_users
    userlink = hlink(message.reply_to_message.from_user.full_name, message.reply_to_message.from_user.url)
    User = ponytypes.UserType(await db_users.find_one({"_id": message.reply_to_message.from_user.id}))
    if User.profile.order is None:
        await message.answer(f"{userlink} не числится в ордене")
        return
    User.updatedb(db_users)
    User.profile.leader = False
    await User.save()
    await message.answer(f"{userlink} был разжалован с поста главы ордена {emoji.emojize(User.profile.order)}")
