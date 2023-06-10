from aiogram import Bot, Dispatcher

import asyncio
import logging

from config.config import get_config
from interface.menu import set_menu_button
from handlers import offline_user_handlers, command_handlers, online_user_handlers
from middlewares import outer_middlewires
from datas.redis_storage import memory_storage, init
from utils.utils import start_clean


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    logger.info('Starting bot')
    await init()
    await start_clean()
    config = get_config()
    storage = await memory_storage()
    bot = Bot(token=config.tg_bot.token_bot)
    dp = Dispatcher(storage=storage)
    dp.include_routers(command_handlers.router, offline_user_handlers.router, online_user_handlers.router)
    dp.message.outer_middleware(outer_middlewires.DataMiddleware())
    dp.callback_query.outer_middleware(outer_middlewires.DataMiddleware())
    dp.startup.register(set_menu_button)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    asyncio.run(main())
