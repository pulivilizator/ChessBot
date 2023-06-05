import chess
import chess.engine
import chess.svg

from interface import keyboards
from chess_engine.svg_to_png import svg_to_png

async def play_game(board: chess.Board, move: str, users):
    if move in [str(m) for m in board.legal_moves]:
        board.push(chess.Move.from_uci(move))
    elif move.replace('q', '') in [str(m) for m in board.legal_moves]:
        board.push(chess.Move.from_uci(move.replace('q', '')))
    else:
        return False, keyboards.InlineKeyboard.create_inline_keyboard(board)
    await svg_to_png(board, users)

    if board.is_game_over():
        return -1

    return keyboards.InlineKeyboard.create_inline_keyboard(board)