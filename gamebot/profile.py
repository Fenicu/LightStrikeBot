import datetime as dt
from re import search

import emoji
from aiogram import types

from support import ponytypes
from support.bothelper import bot


async def UpdateFullProfile(message: types.Message, User: ponytypes.UserType):
    from support.bothelper import db_orders
    datediff: dt.timedelta = message.date - message.forward_date
    if datediff.total_seconds() > 30:
        await message.answer("Пришли мне профиль свежее 30 секунд")
        return
    demoji = emoji.demojize(message.text)
    try:
        _order: str = search(r"(:.*:).* \/order", demoji).group(1)
    except:
        await message.answer("Ты не состоишь в ордене")
        return
    User.profile.stats.power = int(search(r":flexed_biceps:Сила:.*\((\d+)\)", demoji).group(1))
    User.profile.stats.defence = int(search(r":shield:Защита:.*\((\d+)\)", demoji).group(1))
    User.profile.stats.agility = int(search(r":person_running:Прыть:.*\((\d+)\)", demoji).group(1))
    User.profile.stats.instinct = int(search(r":sunglasses:Интуиция:.*\((\d+)\)", demoji).group(1))
    User.profile.stats.life = int(search(r":growing_heart:Живучесть:.*\((\d+)\)", demoji).group(1))
    order = await db_orders.find_one({"_id": _order})
    if not order:
        await message.answer("Ты None чтоли?\nУхади")
        return
    User.profile.order = _order
    User.profile.power = sum(User.profile.stats.values())
    User.profile.original = message.text
    User.profile.updatetime = dt.datetime.now()
    await User.save()
    await message.answer(f"Твой профиль был обновлён\nСумма статов: {User.profile.power}")

async def UpdateSmallProfile(message: types.Message, User: ponytypes.UserType):
    await message.answer("Я принимаю только <code>/full</code> профиль")
