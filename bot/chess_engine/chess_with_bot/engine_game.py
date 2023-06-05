import asyncio
import chess
import chess.engine
import chess.svg
import cairosvg

from interface import keyboards
from chess_engine.svg_to_png import svg_to_png

#engine = chess.engine.SimpleEngine.popen_uci(r"../stockfish/stockfish.exe")
engine = chess.engine.SimpleEngine.popen_uci(r"../stockfish_linux/stockfish-ubuntu.04-x86-64")
async def play_game(board: chess.Board, move: str, user):
    if board.turn == chess.WHITE:

        if move in [str(m) for m in board.legal_moves]:
            board.push(chess.Move.from_uci(move))
        elif move.replace('q', '') in [str(m) for m in board.legal_moves]:
            board.push(chess.Move.from_uci(move.replace('q', '')))
        else:
            return False, keyboards.InlineKeyboard.create_inline_keyboard(board)
    result = engine.play(board, chess.engine.Limit(time=0.1))
    board.push(result.move)
    await svg_to_png()(board, user)
    if board.is_game_over():
        engine.quit()
        return -1

    return keyboards.InlineKeyboard.create_inline_keyboard(board)
