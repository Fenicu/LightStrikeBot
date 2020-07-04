import re
from datetime import datetime as dt

import emoji
from aiogram import types
from loguru import logger

from support import ponytypes

pattern1 = re.compile(r"^:crossed_swords:.*(:.*: и :.*:)", re.MULTILINE) # ⚔️Между 📦 и 🌺
pattern2 = re.compile(r"^:crossed_swords:.*(:.*:)", re.MULTILINE) # ⚔️За 🌿
battletimes = [11, 13, 15, 17, 19, 21]

async def NewGlobalBattleMessage(message: types.Message):
    from support.bothelper import db_battle

    demoji = emoji.demojize(message.caption)
    result = pattern1.findall(demoji)
    if len(result) == 0:
        result = pattern2.findall(demoji)
    if len(result) == 0:
        await message.answer("Я не нашёл битв")
        logger.warning(demoji)
        return
    date = dt.now().hour
    for i in battletimes:
        if date < i:
            nextbattle = dt.now().replace(hour=i, minute=0, second=0, microsecond=0)
            break
    else:
        nextbattle = dt.now().replace(hour=battletimes[0], minute=0, second=0, microsecond=0)
        nextbattle = nextbattle.replace(day=nextbattle.day+1)
    out = f"Битва на {nextbattle.strftime('%d/%m/%Y %H:%M')}\n"
    for fight in result:
        out += fight.replace("и", ":crossed_swords:") + "\n"
    b = await db_battle.find_one({"_id": nextbattle})
    if b:
        await message.answer("Битва уже существует")
    battle = {"_id": nextbattle, "targets": {}}
    for i in result:
        battle["targets"][i] = {}
    #
    await message.answer(emoji.emojize(out))
