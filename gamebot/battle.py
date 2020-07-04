import re
from datetime import datetime as dt
from datetime import timedelta as td

import emoji
from aiogram import types
from loguru import logger

from support import bothelper, ponytypes

pattern1 = re.compile(r"^:crossed_swords:.*(:.*: и :.*:)", re.MULTILINE) # ⚔️Между 📦 и 🌺
pattern2 = re.compile(r"^:crossed_swords:.*(:.*:)", re.MULTILINE) # ⚔️За 🌿
battletimes = [11, 13, 15, 17, 19, 21]

async def NewGlobalBattleMessage(message: types.Message):
    from support.bothelper import db_battle

    datediff: td = message.date - message.forward_date
    if datediff.total_seconds() > 60:
        await message.answer("Сообщение слишком старое")
        return

    demoji = emoji.demojize(message.caption)
    result = pattern1.findall(demoji)
    if len(result) == 0:
        result = pattern2.findall(demoji)
    if len(result) == 0:
        await message.answer("Я не нашёл битв")
        logger.warning(demoji)
        return

    nextbattle = nextbattletime()
    b = await db_battle.find_one({"_id": nextbattle})
    if b:
        await message.answer("Битва уже существует")
        return

    out = f"Битва на {nextbattle.strftime('%d/%m/%Y %H:%M')}\n"
    battle = {"_id": nextbattle, "targets": {}}
    buttons = []
    index = -1

    for fight in result:
        out += fight.replace("и", ":crossed_swords:") + "\n\n"
        index += 1
        battle["targets"][fight] = {}
        buttons.append(types.InlineKeyboardButton(emoji.emojize(fight.replace("и", ":crossed_swords:")),
            callback_data=str({"attack": fight})))
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)

    await db_battle.insert_one(battle)
    msg = await message.answer(emoji.emojize(out), reply_markup=keyboard)
    try:
        await msg.pin(True)
    except:
        pass


async def SendPinToOrder(call: types.CallbackQuery, jsondata: dict, User: ponytypes.UserType):
    from support.bothelper import db_battle
    from support.bothelper import db_chats
    from support.bothelper import db_users

    nextbattle = nextbattletime()
    battle = await db_battle.find_one({"_id": nextbattle})
    if not battle:
        await call.answer("Битва не найдена", True)
        return
    battle = ponytypes.Battle(battle)
    order = await db_chats.find_one({"order": User.profile.order})
    if not order:
        await call.answer("У вашего ордера не назначен чат", True)
        return
    if jsondata["attack"] not in battle.targets:
        await call.answer("Такого направления нет")
        return
    order = ponytypes.ChatType(order)
    order.updatedb(db_chats)
    for k, v in battle.targets.items():
        if User.profile.order in v:
            del battle.targets[k][User.profile.order]
    battle.targets[jsondata["attack"]][User.profile.order] = [] # Пиздец я запаковал это говно
    order.currentpin = jsondata["attack"]
    order.datepin = dt.now()
    await order.save()
    await db_battle.replace_one({"_id": nextbattle}, battle)
    out = f"Битва {nextbattle.strftime('%d/%m/%Y %H:%M')}\nЦель: {order.currentpin}\n\nГотовность:\n"
    power = 0
    sumpower = 0
    async with db_users.find({"profile.order": User.profile.order}).batch_size(10) as cursor:
        async for user in cursor:
            if user["_id"] in battle.targets[order.currentpin][User.profile.order]:
                out += f":white_heavy_check_mark: {user['name']}\n"
                power += user["profile"]["power"]
            else:
                out += f":zzz: {user['name']}\n"
            sumpower += user["profile"]["power"]
    out += f"Сила отряда: {power}/{sumpower}"
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(types.InlineKeyboardButton("Готов", callback_data="ready"))
    msg = await bothelper.bot.send_message(order._id, emoji.emojize(out), reply_markup=keyboard)
    try:
        await msg.pin(True)
    except:
        pass
    await call.answer("Пин отправлен")

async def GetReady(call: types.CallbackQuery, User: ponytypes.UserType):
    from support.bothelper import db_battle
    from support.bothelper import db_chats
    from support.bothelper import db_users

    nextbattle = nextbattletime()
    battle = await db_battle.find_one({"_id": nextbattle})
    if not battle:
        await call.answer("Битва не найдена", True)
        return
    battle = ponytypes.Battle(battle)

    for v in battle.targets.values():
        if User.profile.order in v:
            if call.from_user.id not in v[User.profile.order]:
                v[User.profile.order].append(call.from_user.id)
                await call.answer("Во имя Света!")
                break
            else:
                await call.answer("Ты уже готов!", True)
                return
        else:
            await call.answer("Ожидай нового пина!", True)
            return
    await db_battle.replace_one({"_id": nextbattle}, battle)
    order = await db_chats.find_one({"order": User.profile.order})
    order = ponytypes.ChatType(order)
    out = f"Битва {nextbattle.strftime('%d/%m/%Y %H:%M')}\nЦель: {order.currentpin}\n\nГотовность:\n"
    power = 0
    sumpower = 0
    async with db_users.find({"profile.order": User.profile.order}).batch_size(10) as cursor:
        async for user in cursor:
            if user["_id"] in battle.targets[order.currentpin][User.profile.order]:
                out += f":white_heavy_check_mark: {user['name']}\n"
                power += user["profile"]["power"]
            else:
                out += f":zzz: {user['name']}\n"
            sumpower += user["profile"]["power"]
    out += f"Сила отряда: {power}/{sumpower}"
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(types.InlineKeyboardButton("Готов", callback_data="ready"))
    await call.message.edit_text(emoji.emojize(out), reply_markup=keyboard)
    await call.answer()


def nextbattletime():
    date = dt.now().hour
    for i in battletimes:
        if date < i:
            nextbattle = dt.now().replace(hour=i, minute=0, second=0, microsecond=0)
            break
    else:
        nextbattle = dt.now().replace(hour=battletimes[0], minute=0, second=0, microsecond=0)
        nextbattle = nextbattle.replace(day=nextbattle.day+1)
    return nextbattle
