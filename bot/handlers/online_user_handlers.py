from aiogram import Router, Bot
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.filters import Text, Command, StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext

from chess import Board

from interface import keyboards
from datas.datas import user_data
from chess_engine.chess_with_people import engine_game_online
from lexicon import lexicon
from datas.datas import battle_users
from .FSM import FSMChessGame

router = Router()
users = []


@router.message(Command(commands='play_with_human'), StateFilter(default_state))
@router.message(Text(text=lexicon.LEXICON_COMMANDS_MENU['/play_with_human']), StateFilter(default_state))
async def _start_game(message: Message, bot: Bot, state: FSMContext):
    await message.answer(text='Идет поиск противника, ожидайте')
    if len(users) == 0:
        users.append({
            'p1': {
                'id': message.from_user.id,
                'username': message.from_user.username}})
    else:
        for i in range(len(users)):
            if len(users[i]) == 1:
                users[i].update({
                    'p2': {
                        'id': message.from_user.id,
                        'username': message.from_user.username}})
            print(users)
            await bot.send_message(chat_id=users[i]['p1']['id'],
                                   text=f'Противник найден\nВаш противник: {users[i]["p2"]["username"]}\nВаш цвет: Белый')
            await bot.send_message(chat_id=users[i]['p2']['id'],
                                   text=f'Противник найден\nВаш противник: {users[i]["p1"]["username"]}\nВаш цвет: Черный')
            battle_users[''.join(map(str, [users[i]['p1']['id'], users[i]['p2']['id']]))] = {
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
                                 reply_markup=keyboards.InlineKeyboard.create_inline_keyboard(Board()))
            await bot.send_photo(photo=photo, chat_id=users[i]['p2']['id'],
                                 reply_markup=keyboards.InlineKeyboard.create_inline_keyboard(Board()))
            del users[i]
    await state.set_state(FSMChessGame.chess_online)


@router.message(Command(commands=['play_with_human']), ~StateFilter(default_state))
@router.message(Text(text=lexicon.LEXICON_COMMANDS_MENU['/play_with_human']), ~StateFilter(default_state))
async def _start_error(message: Message):
    await message.answer(text='Вы и так в игре')


@router.callback_query(Text(startswith='TUrNС122'), StateFilter(FSMChessGame.chess_online))
async def _user_turn(clbc: CallbackQuery, state: FSMContext, bot: Bot):
    check_turn, battle_id = await _check_turn(clbc)

    if check_turn is None:
        await clbc.answer(text='Начните игру.')
    elif not check_turn:
        await clbc.answer(text='Не ваш ход')
    else:
        battle_users[battle_id][clbc.from_user.id]['turn'].append(clbc.data)
        print(battle_users)
        if len(battle_users[battle_id][clbc.from_user.id]['turn']) == 2:
            result = await engine_game_online.play_game(board=battle_users[battle_id]['board'],
                                                 move=''.join(battle_users[battle_id][clbc.from_user.id]['turn']).replace('TUrNС122',
                                                                                                            ''),
                                                 users=battle_id)
            photo = FSInputFile(f'../chess_board_screen/{battle_id}.png')
            if isinstance(result, tuple) and not result[0]:
                await clbc.message.answer_photo(photo=photo, caption='Недопустимый ход!',
                                                reply_markup=result[1])
            elif result == -1:
                await clbc.message.answer_photo(photo=photo, caption='Игра окончена!')
                await state.clear()

            else:
                await clbc.message.answer_photo(photo=photo,
                                                reply_markup=result)
                await bot.send_photo(chat_id=battle_id.replace(str(clbc.from_user.id), ''),
                                     photo=photo,
                                     reply_markup=result)
            battle_users[battle_id][clbc.from_user.id]['turn'] = []


async def _get_id(clbc: CallbackQuery):
    if any(str(clbc.from_user.id) in i for i in battle_users.keys()):
        for i in battle_users.keys():
            if str(clbc.from_user.id) in i:
                return i
    return None


async def _check_turn(clbc: CallbackQuery):
    battle_id = await _get_id(clbc)
    if battle_id is None: return None, None
    if battle_id:
        return battle_users[battle_id][clbc.from_user.id]['color'] \
               == \
               battle_users[battle_id]['board'].turn, battle_id
