from aiogram import Router
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.filters import Text, Command

from chess import Board

from ..interface import keyboards
from ..datas.datas import user_data
from ..chess_engine.chess_with_bot import engine_game
from ..lexicon import lexicon

router = Router()
battle_users = []


@router.message(Command(commands='play_with_human'))
@router.message(Text(text=lexicon.LEXICON_COMMANDS_MENU['/play_with_human']))
async def _start_game(message: Message):
    await message.answer(text='Идет поиск противника, ожидайте')


