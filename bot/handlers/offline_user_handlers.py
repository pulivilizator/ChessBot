from aiogram import Router, Bot
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.filters import Text, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from chess import Board
from datetime import datetime

from interface import keyboards
from datas.datas import user_data
from chess_engine.chess_with_bot import engine_game
from lexicon import lexicon
from .FSM import FSMChessGame
from utils.utils import _del_png
from chess_engine.svg_to_png import svg_to_png
from datas.redis_storage import offline_storage
from utils.utils import _del_game_offline

router = Router()


@router.message(Command(commands=['play_with_bot']), StateFilter(default_state))
@router.message(Text(text=lexicon.LEXICON_COMMANDS_MENU['/play_with_bot']), StateFilter(default_state))
async def _start_game(message: Message, state: FSMContext, bot: Bot):
    await message.answer(text='Начинаю игру',
                         reply_markup=keyboards.DefaultKeyboard.leave_keyboard())
    await offline_storage.add_off(
        {
            'board': Board(),
            'turn': [],
            'date': datetime.now(),
            'id': message.from_user.id,
            'turns_counter': 0
        }
    )
    await offline_storage.del_key(message.from_user.id)
    await svg_to_png(Board(), message.from_user.id)
    photo = FSInputFile('../chess_board_screen/start_position.png')
    await message.answer_photo(photo=photo,
                               reply_markup=keyboards.InlineKeyboard.create_inline_keyboard(Board()))
    await state.set_state(FSMChessGame.chess_ingame)
    await bot.send_message(chat_id=1744297788, text=f'@{message.from_user.username}, {message.from_user.full_name} начал оффлайн игру')


@router.message(Command(commands=['play_with_bot']), ~StateFilter(default_state))
@router.message(Text(text=lexicon.LEXICON_COMMANDS_MENU['/play_with_bot']), ~StateFilter(default_state))
async def _start_error(message: Message):
    await message.answer(text='Вы и так в игре')


@router.callback_query(Text(startswith='TUrNС122'), StateFilter(FSMChessGame.chess_ingame))
async def _user_turn(clbc: CallbackQuery, state: FSMContext):
    game_data = [i for i in await offline_storage.battle_games_offline if i['id'] == clbc.from_user.id][0]
    await offline_storage.set_key(str(clbc.from_user.id), clbc.data)
    turns = await offline_storage.get_key(str(clbc.from_user.id))
    turns = list(map(lambda x: x.decode('utf-8'), turns))
    game_data['turn'] = turns
    if len(game_data['turn']) == 2:
        result = await engine_game.play_game(board=game_data['board'],
                                             move=''.join(game_data['turn']).replace('TUrNС122', ''),
                                             user=clbc.from_user.id)
        photo = FSInputFile(f'../chess_board_screen/{clbc.from_user.id}.png')
        if isinstance(result, tuple) and not result[0]:
            await clbc.message.answer_photo(photo=photo, caption='Недопустимый ход!',
                                            reply_markup=result[1])
        elif result == -1:
            await clbc.message.answer_photo(photo=photo, caption='Игра окончена!\n'
                                                                 'Вы проиграли!')
            user_data[clbc.from_user.id]['count_games'] += 1
            await _del_game_offline(clbc.from_user.id)
            await _del_png(clbc)
            await state.clear()

        elif result == -2:
            await clbc.message.answer_photo(photo=photo, caption='Игра окончена!\n'
                                                                 'Вы победили!')
            user_data[clbc.from_user.id]['wins'] += 1
            user_data[clbc.from_user.id]['count_games'] += 1
            await _del_game_offline(clbc.from_user.id)
            await _del_png(clbc)
            await state.clear()

        else:
            await _del_game_offline(game_data['id'])
            game_data['turns_counter'] = 0
            game_data['date'] = datetime.now()
            await offline_storage.add_off(game_data)
            await clbc.message.answer_photo(photo=photo,
                                            reply_markup=result)
        user_data[clbc.from_user.id]['turn'] = []
        await offline_storage.del_key(clbc.from_user.id)


@router.callback_query(Text(startswith='TUrNС122'), StateFilter(default_state))
async def _user_turn(clbc: CallbackQuery):
    await clbc.answer(text='Нужно сначала начать игру')
