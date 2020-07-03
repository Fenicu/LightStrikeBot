from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiomongo import create_client
from loguru import logger

import config

bot = Bot(token=config.Token, validate_token=True, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

client = None
db_chats = None
db_users = None
db_orders = None
settings = None


async def StartDB():
    """
    Запускает сессию драйвера aiomongo
    """

    global client
    global db_chats
    global db_users
    global db_orders
    global settings

    client = await create_client(config.mongoURI)
    db = client.LightBattle
    db_chats = db.Chats
    db_users = db.Users
    db_orders = db.Orders
    settings = db.Settings
    logger.info("database is running")

async def errors(*args):
    """
    Логгирует все ошибки
    """

    logger.error(args[0])
    logger.error(args[1])
    return True

async def NothingCallback(call: types.CallbackQuery):
    logger.warning(f"NothingCallback: {call.data}")
    await call.answer()