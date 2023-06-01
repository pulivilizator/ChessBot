from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from interface import keyboards
from lexicon import lexicon
from datas.datas import user_data

router = Router()


@router.message(CommandStart())
async def _start(message: Message):
    print(message.from_user.username)
    await message.answer(text=lexicon.LEXICON_HANDLER_COMMANDS['/start'],
                         reply_markup=keyboards.DefaultKeyboard.create_default_keyboard())


@router.message(Command(commands=['help']))
async def _help(message: Message):
    await message.answer(text=lexicon.LEXICON_HANDLER_COMMANDS['/help'])


@router.message(Command(commands=['statistic']))
async def _statistic(message: Message):
    await message.answer(text=f'{lexicon.LEXICON_HANDLER_COMMANDS["/statistic"]}'
                              f'Всего игр: {user_data[message.from_user.id]["count_games"]}\n'
                              f'Побед: {user_data[message.from_user.id]["wins"]}')


@router.message(Command(commands=['cancel']))
async def _cancel(message: Message):
    await message.answer(text=lexicon.LEXICON_HANDLER_COMMANDS['/cancel'],
                         reply_markup=keyboards.DefaultKeyboard.create_default_keyboard())
