from aiogram import Router
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.filters import Text, Command

from chess import Board

from interface import keyboards
from datas.datas import user_data
from chess_engine.chess_with_bot import engine_game


router = Router()
turn = []

@router.message(Command(commands=['play']))
@router.message(Text(text='Начать игру'))
async def _start_game(message: Message):
    if not user_data[message.from_user.id]['in_game']:
        user_data[message.from_user.id]['in_game'] = True

        user_data[message.from_user.id]['board'] = Board()
        photo = FSInputFile('../chess_board_screen/start_position.png')
        await message.answer_photo(photo=photo,
                                   reply_markup=keyboards.InlineKeyboard.create_inline_keyboard(
                                       user_data[message.from_user.id]['board']))
    elif user_data[message.from_user.id]['in_game']:
        await message.answer(text='В игре играешь уже')


@router.callback_query(Text(startswith='TUrNС122'))
async def _user_turn(clbc: CallbackQuery):
    global turn
    if user_data[clbc.from_user.id]['in_game']:
        turn.append(clbc.data)
        if len(turn) == 2:
            result = await engine_game.play_game(board=user_data[clbc.from_user.id]['board'],
                                                 move=''.join(turn).replace('TUrNС122', ''),
                                                 user=clbc.from_user.id)
            photo = FSInputFile(f'../chess_board_screen/{clbc.from_user.id}.png')
            if isinstance(result, tuple) and not result[0]:
                await clbc.message.answer_photo(photo=photo, caption='Недопустимый ход!',
                                                reply_markup=result[1])
            elif result == -1:
                await clbc.message.answer_photo(photo=photo, caption='Игра окончена!')
                user_data[clbc.from_user.id]['in_game'] = False

            else:
                await clbc.message.answer_photo(photo=photo,
                                                reply_markup=result)
            turn = []
    else:
        await clbc.answer(text='Игру надо начать сначала')

