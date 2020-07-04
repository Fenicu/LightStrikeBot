from sys import stdout

from aiogram import types
from aiogram.utils.executor import start_webhook
from loguru import logger

import config as cfg
from gamebot.profile import UpdateFullProfile, UpdateSmallProfile
from gamebot.battle import NewGlobalBattleMessage, SendPinToOrder
from orders import register
from support import ponyfilters
from support.bothelper import NothingCallback, bot, dp, errors
from support.middleware import UserMiddleware

logger.remove()
logger.add(stdout, colorize=True, format="<green>{time:DD.MM.YY H:mm:ss}</green> " \
                "| <yellow><b>{level}</b></yellow> | <magenta>{file}</magenta> | <cyan>{message}</cyan>")

dp.middleware.setup(UserMiddleware())
dp.filters_factory.bind(ponyfilters.BotAddFilter, event_handlers=[dp.message_handlers])
dp.filters_factory.bind(ponyfilters.PodGameFilter, event_handlers=[dp.message_handlers])
dp.filters_factory.bind(ponyfilters.JsonCallbackDataFilter, event_handlers=[dp.callback_query_handlers])
dp.filters_factory.bind(ponyfilters.LeaderFilter, event_handlers=[dp.message_handlers, dp.callback_query_handlers])
dp.filters_factory.bind(ponyfilters.AdminFilter, event_handlers=[dp.message_handlers, dp.callback_query_handlers])

dp.register_message_handler(NewGlobalBattleMessage, is_botadmin=True, is_pod=True,
    content_types=types.ContentTypes.PHOTO, regexp=r"Плодородные земли")
dp.register_callback_query_handler(SendPinToOrder, is_leader=True, json_check="attack")

dp.register_message_handler(register.NewChat, is_addbot=True, content_types=types.ContentTypes.NEW_CHAT_MEMBERS)
dp.register_message_handler(UpdateFullProfile, types.ChatType.is_private, is_pod=True, regexp=r"Компактный профиль \/compact")
dp.register_message_handler(UpdateSmallProfile, types.ChatType.is_private, is_pod=True, regexp=r"Полный профиль \/full")
dp.register_message_handler(register.RegisterNewOrder, is_botadmin=True, commands=["create_order"])
dp.register_message_handler(register.DeleteOrder, is_botadmin=True, commands=["delete_order"])
dp.register_message_handler(register.NewLeader, types.ChatType.is_group_or_super_group,
    is_reply=True, is_botadmin=True, commands=["new_leader"])
dp.register_message_handler(register.RemoveLeader, types.ChatType.is_group_or_super_group,
    is_reply=True, is_botadmin=True, commands=["del_leader"])

#dp.register_errors_handler(errors)
dp.register_callback_query_handler(NothingCallback)

async def on_startup(dp):
    from support.bothelper import StartDB
    await StartDB()
    await bot.set_webhook(cfg.WEBHOOK_URL)
    botinfo = await bot.me
    logger.info(f"Бот {botinfo.full_name} запущен")

async def on_shutdown(dp):
    from support.bothelper import client
    logger.warning('Shutting down..')
    await bot.delete_webhook()
    client.close()
    await client.wait_closed()
    logger.warning('Bye!')

if __name__ == "__main__":
    start_webhook(
        dispatcher=dp,
        webhook_path="",
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host='127.0.0.1',
        port=cfg.WEBHOOK_PORT)
