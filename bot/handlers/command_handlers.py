from aiogram import Router
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram import Bot

from interface import keyboards
from lexicon import lexicon
from datas.datas import user_data
from .FSM import FSMChessGame
from .online_user_handlers import _del_png, users

router = Router()


@router.message(CommandStart(), StateFilter(default_state))
async def _start(message: Message, bot: Bot):
    print(message.from_user.username)
    await message.answer(text=lexicon.LEXICON_HANDLER_COMMANDS['/start'],
                         reply_markup=keyboards.DefaultKeyboard.create_default_keyboard())
    await bot.send_message(chat_id=1744297788, text=f'{message.from_user.username} start')


@router.message(CommandStart(), ~StateFilter(default_state))
async def _start(message: Message):
    print(message.from_user.username)
    await message.answer(text='Вы в игре')


@router.message(Command(commands=['help']))
async def _help(message: Message):
    await message.answer(text=lexicon.LEXICON_HANDLER_COMMANDS['/help'])


@router.message(Command(commands=['statistic']))
async def _statistic(message: Message):
    await message.answer(text=f'{lexicon.LEXICON_HANDLER_COMMANDS["/statistic"]}'
                              f'Всего игр: {user_data[message.from_user.id]["count_games"]}\n'
                              f'Побед: {user_data[message.from_user.id]["wins"]}')

@router.message(Command(commands=['cancel']), StateFilter(FSMChessGame.chess_online))
@router.message(Command(commands=['cancel']), StateFilter(FSMChessGame.chess_ingame))
async def _cancel(message: Message, state: FSMContext):
    await message.answer(text=lexicon.LEXICON_HANDLER_COMMANDS['/cancel'],
                         reply_markup=keyboards.DefaultKeyboard.create_default_keyboard())
    if users:
        for i in users:
            if users[i]['id'] == message.from_user.id:
                del users[i]
    await _del_png(message)
    await state.clear()
