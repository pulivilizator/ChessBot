from aiogram import Router, Bot
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.filters import Text, Command, StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext

from chess import Board
import os

from interface import keyboards
from chess_engine.chess_with_people import engine_game_online
from lexicon import lexicon
from datas.datas import battle_users, user_data
from .FSM import FSMChessGame
from chess_engine.svg_to_png import svg_to_png

router = Router()
users = []


@router.message(Command(commands='play_with_human'), StateFilter(default_state))
@router.message(Text(text=lexicon.LEXICON_COMMANDS_MENU['/play_with_human']), StateFilter(default_state))
async def _start_game(message: Message, bot: Bot, state: FSMContext):
    await message.answer(text='Идет поиск противника, ожидайте',
                         reply_markup=keyboards.DefaultKeyboard.game_stat_keyboard())
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
            await bot.send_message(chat_id=users[i]['p1']['id'],
                                   text=f'Противник найден\nВаш противник: @{users[i]["p2"]["username"]}\nВаш цвет: Белый')
            await bot.send_message(chat_id=users[i]['p2']['id'],
                                   text=f'Противник найден\nВаш противник: @{users[i]["p1"]["username"]}\nВаш цвет: Черный')
            battle_id = ''.join(map(str, [users[i]['p1']['id'], users[i]['p2']['id']]))
            await svg_to_png(Board(), battle_id)
            battle_users[battle_id] = {
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
    await bot.send_message(chat_id=1744297788, text=f'@{message.from_user.username} начал онлайн игру')


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
                                                        move=''.join(battle_users[battle_id][clbc.from_user.id]['turn'])
                                                        .replace('TUrNС122', ''),
                                                        users=battle_id)

            photo = FSInputFile(f'../chess_board_screen/{battle_id}.png')
            if isinstance(result, tuple) and not result[0]:
                await clbc.message.answer_photo(photo=photo, caption='Недопустимый ход!',
                                                reply_markup=result[1])

            elif result == -1:
                del battle_users[battle_id]
                await clbc.message.answer_photo(photo=photo, caption='Игра окончена!\n'
                                                                     'Вы победили!')
                await bot.send_photo(chat_id=battle_id.replace(str(clbc.from_user.id), ''),
                                     caption='Игра окончена!\n'
                                             'Вы проиграли\n'
                                             'Для выхода из игры нажмите кнопку.',
                                     photo=photo,
                                     reply_markup=keyboards.DefaultKeyboard.leave_keyboard())
                user_data[clbc.from_user.id]['wins'] += 1
                user_data[clbc.from_user.id]['count_games'] += 1
                user_data[int(battle_id.replace(str(clbc.from_user.id), ''))]['count_games'] += 1
                await _del_png(clbc)
                await state.clear()

            else:
                await clbc.message.answer_photo(photo=photo,
                                                caption='Ход противника!')
                await bot.send_photo(chat_id=battle_id.replace(str(clbc.from_user.id), ''),
                                     caption='Ваш ход!\n'
                                             'Ваш цвет: Белый'
                                     if not battle_users[battle_id][clbc.from_user.id]['color']
                                     else 'Ваш ход!\n'
                                          'Ваш цвет: Черный',
                                     photo=photo,
                                     reply_markup=result)
            battle_users[battle_id][clbc.from_user.id]['turn'] = []


async def _get_id(clbc: CallbackQuery | Message) -> str | None:
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


async def _del_png(clbc: CallbackQuery | Message) -> None:
    folder_path = '../chess_board_screen'
    files = os.listdir(folder_path)
    for file in files:
        if str(clbc.from_user.id) in file:
            file_path = os.path.join(folder_path, file)
            os.remove(file_path)
