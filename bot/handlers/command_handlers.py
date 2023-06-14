from aiogram import Router
from aiogram.filters import CommandStart, Command, StateFilter, Text
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram import Bot

from interface import keyboards
from lexicon import lexicon
from datas.db import client
from .FSM import FSMChessGame
from .online_user_handlers import users, _get_game
from utils.utils import _del_png, _del_game, _del_game_offline

router = Router()


@router.message(CommandStart(), StateFilter(default_state))
async def _start(message: Message, bot: Bot):
    print(message.from_user.username)
    await message.answer(text=lexicon.LEXICON_HANDLER_COMMANDS['/start'],
                         reply_markup=keyboards.DefaultKeyboard.create_default_keyboard())
    await bot.send_message(chat_id=1744297788,
                           text=f'@{message.from_user.username}, {message.from_user.full_name} start')


@router.message(CommandStart(), ~StateFilter(default_state))
async def _start(message: Message):
    print(message.from_user.username)
    await message.answer(text='Вы в игре')


@router.message(Command(commands=['help']))
async def _help(message: Message):
    await message.answer(text=lexicon.LEXICON_HANDLER_COMMANDS['/help'])


@router.message(Command(commands=['statistic']))
async def _statistic(message: Message):
    stat = await client.fetch(f"""SELECT *
                                  FROM users
                                  WHERE user_id = {message.from_user.id}""")
    stat = stat[0]
    await message.answer(text=f'{lexicon.LEXICON_HANDLER_COMMANDS["/statistic"]}'
                              f'Всего игр: {stat["count_games"]}\n'
                              f'Побед: {stat["wins"]}\n'
                              f'Покинуто игр: {stat["leave"]}')


@router.message(Command(commands=['rival_stat']), StateFilter(FSMChessGame.chess_online))
@router.message(Text(text=lexicon.LEXICON_COMMANDS_MENU['/rival_stat']), StateFilter(FSMChessGame.chess_online))
async def _rival_stat(message: Message):
    battle_game = await _get_game(message)
    if battle_game:
        rival_id = int(battle_game['battle_id'].replace(str(message.from_user.id), ''))
        stat = await client.fetch(f"""SELECT *
                                      FROM users
                                      WHERE user_id = {rival_id}""")
        stat = stat[0]
        await message.answer(text=f'Статистика соперника: {stat["username"]}\n'
                                  f'Всего игр: {stat["count_games"]}\n'
                                  f'Побед: {stat["wins"]}\n'
                                  f'Покинуто игр: {stat["leave"]}')
    elif battle_game is None:
        await message.answer(text='Соперник еще не найден')


@router.message(Command(commands=['rival_stat']), ~StateFilter(FSMChessGame.chess_online))
@router.message(Text(text=lexicon.LEXICON_COMMANDS_MENU['/rival_stat']), ~StateFilter(FSMChessGame.chess_online))
async def _rival_stat(message: Message):
    await message.answer(text='Сначала найдите соперника.')


@router.message(Text(text=lexicon.LEXICON_COMMANDS_MENU['/cancel']), StateFilter(FSMChessGame.chess_online))
@router.message(Command(commands=['cancel']), StateFilter(FSMChessGame.chess_online))
async def _cancel(message: Message, state: FSMContext, bot: Bot):
    await message.answer(text=lexicon.LEXICON_HANDLER_COMMANDS['/cancel'],
                         reply_markup=keyboards.DefaultKeyboard.create_default_keyboard())
    battle_game = await _get_game(message)
    if battle_game:
        await bot.send_message(chat_id=battle_game['battle_id'].replace(str(message.from_user.id), ''),
                               text='Соперник завершил игру.\n'
                                    'Для выхода нажмите на кнопку.',
                               reply_markup=keyboards.DefaultKeyboard.leave_keyboard())
        await client.execute(f"""UPDATE users
                                 SET leave=leave + 1
                                 WHERE user_id={message.from_user.id};""")
        await _del_game(battle_game['battle_id'])
    for i in range(len(users)):
        if message.from_user.id == users[i]['p1']['id']:
            del users[i]
    await _del_png(message)
    await state.clear()


@router.message(Text(text=lexicon.LEXICON_COMMANDS_MENU['/cancel']), StateFilter(FSMChessGame.chess_ingame))
@router.message(Command(commands=['cancel']), StateFilter(FSMChessGame.chess_ingame))
async def _cancel(message: Message, state: FSMContext):
    await message.answer(text=lexicon.LEXICON_HANDLER_COMMANDS['/cancel'],
                         reply_markup=keyboards.DefaultKeyboard.create_default_keyboard())
    await _del_game_offline(message.from_user.id)
    await _del_png(message)
    await state.clear()


@router.message(Text(text=lexicon.LEXICON_COMMANDS_MENU['/cancel']), ~StateFilter(FSMChessGame.chess_online))
@router.message(Text(text=lexicon.LEXICON_COMMANDS_MENU['/cancel']), ~StateFilter(FSMChessGame.chess_ingame))
@router.message(Command(commands=['cancel']), ~StateFilter(FSMChessGame.chess_online))
@router.message(Command(commands=['cancel']), ~StateFilter(FSMChessGame.chess_ingame))
async def _cancel(message: Message, ):
    await message.answer(text=lexicon.LEXICON_HANDLER_COMMANDS['/cancel'],
                         reply_markup=keyboards.DefaultKeyboard.create_default_keyboard())
