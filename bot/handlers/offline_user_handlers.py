from aiogram import Router
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.filters import Text, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from chess import Board

from interface import keyboards
from datas.datas import user_data
from chess_engine.chess_with_bot import engine_game
from lexicon import lexicon
from .FSM import FSMChessGame
from .online_user_handlers import _del_png

router = Router()


@router.message(Command(commands=['play_with_bot']), StateFilter(default_state))
@router.message(Text(text=lexicon.LEXICON_COMMANDS_MENU['/play_with_bot']), StateFilter(default_state))
async def _start_game(message: Message, state: FSMContext):
    user_data[message.from_user.id]['in_game'] = True

    user_data[message.from_user.id]['board'] = Board()
    photo = FSInputFile('../chess_board_screen/start_position.png')
    await message.answer_photo(photo=photo,
                               reply_markup=keyboards.InlineKeyboard.create_inline_keyboard(
                                   user_data[message.from_user.id]['board']))
    await state.set_state(FSMChessGame.chess_ingame)


@router.message(Command(commands=['play_with_bot']), ~StateFilter(default_state))
@router.message(Text(text=lexicon.LEXICON_COMMANDS_MENU['/play_with_bot']), ~StateFilter(default_state))
async def _start_error(message: Message):
    await message.answer(text='Вы и так в игре')


@router.callback_query(Text(startswith='TUrNС122'), StateFilter(FSMChessGame.chess_ingame))
async def _user_turn(clbc: CallbackQuery, state: FSMContext):
    user_data[clbc.from_user.id]['turn'].append(clbc.data)
    if len(user_data[clbc.from_user.id]['turn']) == 2:
        result = await engine_game.play_game(board=user_data[clbc.from_user.id]['board'],
                                             move=''.join(user_data[clbc.from_user.id]['turn']).replace('TUrNС122', ''),
                                             user=clbc.from_user.id)
        photo = FSInputFile(f'../chess_board_screen/{clbc.from_user.id}.png')
        if isinstance(result, tuple) and not result[0]:
            await clbc.message.answer_photo(photo=photo, caption='Недопустимый ход!',
                                            reply_markup=result[1])
        elif result == -1:
            await clbc.message.answer_photo(photo=photo, caption='Игра окончена!\n'                                                       'Вы проиграли!')
            user_data[clbc.from_user.id]['count_games'] += 1
            await _del_png(clbc)
            await state.clear()

        elif result == -2:
            await clbc.message.answer_photo(photo=photo, caption='Игра окончена!\n'
                                                                 'Вы победили!')
            user_data[clbc.from_user.id]['wins'] += 1
            user_data[clbc.from_user.id]['count_games'] += 1
            await _del_png(clbc)
            await state.clear()

        else:
            await clbc.message.answer_photo(photo=photo,
                                            reply_markup=result)
        user_data[clbc.from_user.id]['turn'] = []


@router.callback_query(Text(startswith='TUrNС122'), StateFilter(default_state))
async def _user_turn(clbc: CallbackQuery):
    await clbc.answer(text='Нужно сначала начать игру')
