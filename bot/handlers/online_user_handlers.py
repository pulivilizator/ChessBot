from aiogram import Router, Bot
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.filters import Text, Command, StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext

from chess import Board
from datetime import datetime

from interface import keyboards
from chess_engine.chess_with_people import engine_game_online
from lexicon import lexicon
from datas.db import client
from datas.redis_storage import storage
from .FSM import FSMChessGame
from chess_engine.svg_to_png import svg_to_png
from utils.utils import _del_png, _del_game

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
            await storage.add({
                users[i]['p1']['id']: {
                    'color': True,
                    'turn': []
                },
                users[i]['p2']['id']: {
                    'color': False,
                    'turn': []
                },
                'board': Board(),
                'date': datetime.now(),
                'battle_id': battle_id,
                'turns_counter': 0
            })
            photo = FSInputFile('../chess_board_screen/start_position.png')
            await bot.send_photo(photo=photo, chat_id=users[i]['p1']['id'],
                                 reply_markup=keyboards.InlineKeyboard.create_inline_keyboard(Board()))
            await bot.send_photo(photo=photo, chat_id=users[i]['p2']['id'])
            await storage.del_key(users[i]['p1']['id'])
            await storage.del_key(users[i]['p2']['id'])
            del users[i]
    await state.set_state(FSMChessGame.chess_online)
    await bot.send_message(chat_id=1744297788, text=f'@{message.from_user.username}, {message.from_user.full_name} ожидает соперника')
    await bot.send_message(chat_id=464437438, text=f'@{message.from_user.username}, {message.from_user.full_name} ожидает соперника')


@router.message(Command(commands=['play_with_human']), ~StateFilter(default_state))
@router.message(Text(text=lexicon.LEXICON_COMMANDS_MENU['/play_with_human']), ~StateFilter(default_state))
async def _start_error(message: Message):
    await message.answer(text='Вы и так в игре')


@router.callback_query(Text(startswith='TUrNС122'), StateFilter(FSMChessGame.chess_online))
async def _user_turn(clbc: CallbackQuery, state: FSMContext, bot: Bot):
    check_turn, battle_game = await _check_turn(clbc)
    battle_id = battle_game['battle_id']
    if check_turn is None:
        await clbc.answer(text='Начните игру.')
    elif not check_turn:
        await clbc.answer(text='Не ваш ход')
    else:
        await storage.set_key(str(clbc.from_user.id), clbc.data)
        turns = await storage.get_key(str(clbc.from_user.id))
        turns = list(map(lambda x: x.decode('utf-8'), turns))
        battle_game[clbc.from_user.id]['turn'] = turns
        print(battle_game)
        print(battle_game['date'])
        if len(battle_game[clbc.from_user.id]['turn']) == 2:
            result = await engine_game_online.play_game(board=battle_game['board'],
                                                        move=''.join(battle_game[clbc.from_user.id]['turn'])
                                                        .replace('TUrNС122', ''),
                                                        users=battle_id)

            photo = FSInputFile(f'../chess_board_screen/{battle_id}.png')
            if isinstance(result, tuple) and not result[0]:
                await clbc.message.answer_photo(photo=photo, caption='Недопустимый ход!',
                                                reply_markup=result[1])

            elif result == -1:
                battle_games = await _del_game(battle_id)
                await storage.overwriting(battle_games)
                await clbc.message.answer_photo(photo=photo, caption='Игра окончена!\n'
                                                                     'Вы победили!')
                await bot.send_photo(chat_id=battle_id.replace(str(clbc.from_user.id), ''),
                                     caption='Игра окончена!\n'
                                             'Вы проиграли\n'
                                             'Для выхода из игры нажмите кнопку.',
                                     photo=photo,
                                     reply_markup=keyboards.DefaultKeyboard.leave_keyboard())
                await client.execute(f"""UPDATE users
                                         SET count_games = count_games + 1, wins = wins + 1
                                         WHERE user_id={clbc.from_user.id};""")
                await client.execute(f"""UPDATE users
                                         SET count_games = count_games + 1
                                         WHERE user_id={int(battle_id.replace(str(clbc.from_user.id), ''))};""")
                await client.close()
                await _del_png(clbc)
                await state.clear()

            else:
                if not battle_game['turns_counter'] % 3:
                    await _del_game(battle_id)
                    battle_game['turns_counter'] = 0
                    battle_game['date'] = datetime.now()
                    await storage.add(battle_game)
                await clbc.message.answer_photo(photo=photo,
                                                caption='Ход противника!')
                await bot.send_photo(chat_id=battle_id.replace(str(clbc.from_user.id), ''),
                                     caption='Ваш ход!\n'
                                             'Ваш цвет: Белый'
                                     if not battle_game[clbc.from_user.id]['color']
                                     else 'Ваш ход!\n'
                                          'Ваш цвет: Черный',
                                     photo=photo,
                                     reply_markup=result)
                battle_game['turns_counter'] += 1
            await storage.del_key(str(clbc.from_user.id))
            await storage.del_key(battle_id.replace(str(clbc.from_user.id), ''))
            battle_game[clbc.from_user.id]['turn'] = []


async def _get_game(clbc: CallbackQuery | Message) -> dict | None:
    for game in await storage.battle_games:
        if clbc.from_user.id in game:
            return game
    return None


async def _check_turn(clbc: CallbackQuery):
    battle_game = await _get_game(clbc)
    if battle_game is None: return None, None
    return battle_game[clbc.from_user.id]['color'] \
           == \
           battle_game['board'].turn, battle_game


async def _counter_turns(clbk: CallbackQuery):
    if not await storage.get_key(str(clbk.from_user.id)):
        await storage.set_key(str(clbk.from_user.id), clbk.data)
    else:
        first_turn = await storage.get_key(str(clbk.from_user.id))
        first_turn = first_turn.decode('utf-8')
        return [first_turn, clbk.data]




