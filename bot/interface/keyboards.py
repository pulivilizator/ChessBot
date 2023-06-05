from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from lexicon import lexicon
from chess import Board


class InlineKeyboard:
    pole: list = [[1 if not i % 2 and j % 2
                   else
                   1 if i % 2 and not j % 2
                   else 0
                   for i in range(8)] for j in range(8)]

    @classmethod
    def _chess_board_formatter(cls, board, i, j) -> InlineKeyboardButton:
        cell = f'TUrNС122{chr(j + 97)}{abs(i + 1 - 9)}'
        if i == 0 or i == 7:
            cell = cell + 'q'
        figure = board[i][j]
        if figure != '.':
            return InlineKeyboardButton(text=lexicon.LEXICON_FIGURES[figure],
                                        callback_data=cell)

        return InlineKeyboardButton(text=lexicon.LEXICON_FIGURES[cls.pole[i][j]],
                                    callback_data=cell)

    @classmethod
    def create_inline_keyboard(cls, board: Board) -> InlineKeyboardMarkup:
        game_board = str(board).replace(' ', '').split('\n')
        buttons: list = []
        kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
        for i in range(len(game_board)):
            for j in range(len(game_board[i])):
                buttons.append(cls._chess_board_formatter(game_board, i, j))

        kb_builder.row(*buttons, width=8)
        return kb_builder.as_markup()


class DefaultKeyboard:
    @classmethod
    def create_default_keyboard(cls) -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=lexicon.LEXICON_COMMANDS_MENU['/play_with_bot'])],
                                             [KeyboardButton(text=lexicon.LEXICON_COMMANDS_MENU['/play_with_human'])]],
                                   resize_keyboard=True, one_time_keyboard=True)
