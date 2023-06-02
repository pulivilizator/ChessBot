from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from datas.datas import user_data
from chess_engine.chess_with_bot.engine_game import _refr_to_png

from chess import Board


class DataMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message | CallbackQuery, data):
        if isinstance(event, Message) and event.from_user.id not in user_data:
            user_data[event.from_user.id] = {'in_game': False,
                                             'board': Board(),
                                             'wins': 0,
                                             'count_games': 0}
        elif isinstance(event, CallbackQuery) and event.from_user.id not in user_data:
            user_data[event.from_user.id] = {'in_game': False,
                                             'board': Board(),
                                             'wins': 0,
                                             'count_games': 0}
        await _refr_to_png(Board(), event.from_user.id)
        return await handler(event, data)
