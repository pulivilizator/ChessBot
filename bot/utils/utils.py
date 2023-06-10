from aiogram.types import Message, CallbackQuery

from datetime import datetime, timedelta
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from datas.redis_storage import storage

async def _del_png(clbc: CallbackQuery | Message) -> None:
    folder_path = '../chess_board_screen'
    files = os.listdir(folder_path)
    for file in files:
        if str(clbc.from_user.id) in file:
            file_path = os.path.join(folder_path, file)
            os.remove(file_path)

async def _del_game(battle_id):
    await storage.overwriting([i for i in await storage.battle_games if i['battle_id'] != battle_id])

async def _del_game_offline(battle_id):
    await storage.overwriting([i for i in await storage.battle_games_offline if i['id'] != battle_id])


async def cleaner():
    for i in await storage.battle_games:
        if datetime.now() - i['date'] > timedelta(hours=24):
            await _del_game(i['battle_id'])
    for i in await storage.battle_games_offline:
        if datetime.now() - i['date'] > timedelta(hours=24):
            await _del_game_offline(i['id'])

async def start_clean():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(cleaner, 'interval', hours=24)
    scheduler.start()
