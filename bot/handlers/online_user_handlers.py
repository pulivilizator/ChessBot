from aiogram import Router, Bot
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.filters import Text, Command, StateFilter
from aiogram.fsm.state import default_state

from chess import Board

from ..interface import keyboards
from ..datas.datas import user_data
from ..chess_engine.chess_with_bot import engine_game
from ..lexicon import lexicon
from ..datas.datas import battle_users
from .FSM import FSMChessGame
from ..chess_engine.chess_with_bot.engine_game import _refr_to_png

router = Router()
users = []


@router.message(Command(commands='play_with_human'), StateFilter(default_state))
@router.message(Text(text=lexicon.LEXICON_COMMANDS_MENU['/play_with_human']), StateFilter(default_state))
async def _start_game(message: Message, bot: Bot):
    await message.answer(text='Идет поиск противника, ожидайте')
    if len(users) == 0:
        users.append([{
            'p1': {
                'id': message.from_user.id,
                'username': message.from_user.username}}])
    else:
        for i in range(len(users)):
            if len(users[i]) == 1:
                users[i].append({
                    'p2': {
                        'id': message.from_user.id,
                        'username': message.from_user.username}})
            await bot.send_message(chat_id=users[i]['p1']['id'],
                                   text=f'Противник найден\nВаш противник: {users[i]["p2"]["username"]}')
            await bot.send_message(chat_id=users[i]['p2']['id'],
                                   text=f'Противник найден\nВаш противник: {users[i]["p1"]["username"]}')
            battle_users[''.join(users[i])] = {
                users[i]['p1']['id']: {
                    'color': True,
                    'turn': []
                },
                users[i]['p2']['id']: {
                    'color': False,
                    'turn': []
                },
                'board': Board()
            }
            photo = FSInputFile('../chess_board_screen/start_position.png')
            await bot.send_photo(photo=photo, chat_id=users[i]['p1']['id'],
                                 reply_markup=keyboards.InlineKeyboard.create_inline_keyboard(
                                     battle_users[''.join(users[i])]['board']))
            await bot.send_photo(photo=photo, chat_id=users[i]['p2']['id'],
                                 reply_markup=keyboards.InlineKeyboard.create_inline_keyboard(
                                     battle_users[''.join(users[i])]['board']))
            del users[i]
