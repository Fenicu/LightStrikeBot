from sys import stdout

from aiogram import types
from aiogram.utils.executor import start_webhook
from loguru import logger

import config as cfg
from support.middleware import UserMiddleware
from support.bothelper import bot, dp, errors, NothingCallback

logger.remove()
logger.add(stdout, colorize=True, format="<green>{time:DD.MM.YY H:mm:ss}</green> " \
                "| <yellow><b>{level}</b></yellow> | <magenta>{file}</magenta> | <cyan>{message}</cyan>")

dp.middleware.setup(UserMiddleware())

dp.register_errors_handler(errors)
dp.register_callback_query_handler(NothingCallback)

async def on_startup(dp):
    from support.bothelper import StartDB
    await StartDB()
    await bot.set_webhook(cfg.WEBHOOK_URL)


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
