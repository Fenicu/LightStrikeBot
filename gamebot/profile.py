import re
from re import search
import datetime as dt
from aiogram import types

from support import ponytypes
from support.bothelper import bot

RE_EMOJI = re.compile("["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)

async def UpdateFullProfile(message: types.Message, User: ponytypes.UserType):
    from support.bothelper import db_orders
    _order: str = RE_EMOJI.findall(message.text)[0]
    User.profile.stats.power = int(search(r"💪Сила:.*\((\d+)\)", message.text).group(1))
    User.profile.stats.defence = int(search(r"🛡Защита:.*\((\d+)\)", message.text).group(1))
    User.profile.stats.agility = int(search(r"🏃Прыть:.*\((\d+)\)", message.text).group(1))
    User.profile.stats.instinct = int(search(r"🕶Интуиция:.*\((\d+)\)", message.text).group(1))
    User.profile.stats.life = int(search(r"💗Живучесть:.*\((\d+)\)", message.text).group(1))
    order = await db_orders.find_one({"icon": _order})
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
    from support.bothelper import db_orders
    _order: str = RE_EMOJI.findall(message.text)[0]
    User.profile.stats.power = int(search(r"💪 (\d+)", message.text).group(1))
    User.profile.stats.defence = int(search(r"🛡 (\d+)", message.text).group(1))
    User.profile.stats.agility = int(search(r"🏃 (\d+)", message.text).group(1))
    User.profile.stats.instinct = int(search(r"🕶 (\d+)", message.text).group(1))
    User.profile.stats.life = int(search(r"💗 (\d+)", message.text).group(1))
    order = await db_orders.find_one({"icon": _order})
    if not order:
        await message.answer("Ты None чтоли?\nУхади")
        return
    User.profile.order = _order
    User.profile.power = sum(User.profile.stats.values())
    User.profile.original = message.text
    User.profile.updatetime = dt.datetime.now()
    await User.save()
    await message.answer(f"Твой профиль был обновлён\nСумма статов: {User.profile.power}")
