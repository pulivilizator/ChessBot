from aiogram.filters.state import State, StatesGroup


class FSMChessGame(StatesGroup):
    chess_ingame = State()
    chess_online = State()

