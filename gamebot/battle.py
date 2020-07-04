import re
from datetime import datetime as dt
from datetime import timedelta as td

import emoji
from aiogram import types
from loguru import logger

from support import ponytypes, bothelper

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

    nextbattle = nextbattletime()
    battle = await db_battle.find_one({"_id": nextbattle})
    if not battle or battle["_id"] != nextbattle:
        await call.answer("Битва не найдена", True)
        return
    battle = ponytypes.Battle(battle)
    order = await db_chats.find_one({"order": User.profile.order})
    if not order:
        await call.answer("У вашего ордера не назначен чат", True)
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
    out = f"Битва {nextbattle.strftime('%d/%m/%Y %H:%M')}\nЦель: {order.currentpin}"
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(types.InlineKeyboardButton("Готовность", callback_data="ready"))
    msg = await bothelper.bot.send_message(order._id, emoji.emojize(out), reply_markup=keyboard)
    try:
        await msg.pin(True)
    except:
        pass
    await call.answer("Пин отправлен")


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