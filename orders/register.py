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


async def RegisterNewOrder(message: types.Message):
    from support.bothelper import db_orders
    order_icon = message.get_args()
    order = await db_orders.find_one({"_id": order_icon})
    if order:
        await message.answer("Такой ордер уже существует, ты чо, пёс")
        return
    order = {"_id": order_icon}
    await db_orders.insert_one(order)
    await message.answer(f"Ордер {order_icon} был сохранён")

async def DeleteOrder(message: types.Message):
    from support.bothelper import db_orders
    order_icon = message.get_args()
    result = await db_orders.delete_one({"_id": order_icon})
    if result.deleted_count > 0:
        await message.answer(f"Ордер: {order_icon} был удалён")
        return
    await message.answer("Такого ордера нет")