from aiogram.types import Message, FSInputFile, CallbackQuery

from datetime import datetime, timedelta
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from datas.redis_storage import storage
from handlers.online_user_handlers import _del_game

async def _del_png(clbc: CallbackQuery | Message) -> None:
    folder_path = '../chess_board_screen'
    files = os.listdir(folder_path)
    for file in files:
        if str(clbc.from_user.id) in file:
            file_path = os.path.join(folder_path, file)
            os.remove(file_path)


async def cleaner():
    for i in await storage.battle_games:
        if datetime.now() - i['date'] > timedelta(hours=24):
            await _del_game(i['battle_id'])

async def start_clean():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(cleaner, 'interval', hours=24)
    scheduler.start()
