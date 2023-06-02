from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from datas.datas import user_data
from chess import Board


class DataMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message | CallbackQuery, data):
        if isinstance(event, Message) and event.from_user.id not in user_data:
            user_data[event.from_user.id] = {'in_game': False,
                                             'turns': 0,
                                             'board': Board(),
                                             'wins': 0,
                                             'count_games': 0}
        elif isinstance(event, CallbackQuery) and event.from_user.id not in user_data:
            user_data[event.from_user.id] = {'in_game': False,
                                             'turns': 0,
                                             'board': Board(),
                                             'wins': 0,
                                             'count_games': 0}
        return await handler(event, data)
