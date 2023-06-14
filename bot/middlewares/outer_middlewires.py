from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from chess_engine.svg_to_png import svg_to_png
from datas.db import client
from datas.redis_storage import RedisBattleStorage

from chess import Board
from typing import Iterator

r_storage = RedisBattleStorage(db=2)


class DataMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message | CallbackQuery, data):
        redis_result = await r_storage.redis.get(str(event.from_user.id))
        if not redis_result:
            db_result = await client.execute(f"""SELECT *
                                                 FROM users
                                                 WHERE user_id = {event.from_user.id}""")
            if not db_result:
                await client.execute(f"""INSERT INTO users (username, user_id, wins, count_games, leave)
                                         VALUES ('@{event.from_user.username}', {event.from_user.id}, 0, 0, 0)""")
                await r_storage.redis.set(str(event.from_user.id), 1)
                await r_storage.redis.expire(str(event.from_user.id), 7200)
                await svg_to_png(Board(), event.from_user.id)
            elif db_result:
                await r_storage.redis.set(str(event.from_user.id), 1)
                await r_storage.redis.expire(str(event.from_user.id), 7200)

        return await handler(event, data)
