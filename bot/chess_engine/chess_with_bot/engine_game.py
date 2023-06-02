import asyncio
import chess
import chess.engine
import chess.svg
import aspose.words as aw
import cairosvg

from interface import keyboards

engine = chess.engine.SimpleEngine.popen_uci(r"../stockfish_linux/stockfish-ubuntu.04-x86-64")
async def play_game(board: chess.Board, move: str, user):
    if board.is_game_over():
        engine.quit()
        return -1
    if board.turn == chess.WHITE:

        if move in [str(m) for m in board.legal_moves]:
            board.push(chess.Move.from_uci(move))
        else:
            return False, keyboards.InlineKeyboard.create_inline_keyboard(board)
    result = engine.play(board, chess.engine.Limit(time=0.1))
    board.push(result.move)
    await _refrtopng(board, user)

    return keyboards.InlineKeyboard.create_inline_keyboard(board)




async def _refrtopng(board, user):
    with open(f'../chess_board_screen/{user}.svg', 'w') as file:
        file.write(chess.svg.board(board, size=1000))

    svg_file_path = f"../chess_board_screen/{user}.svg"


    png_file_path = f"../chess_board_screen/{user}.png"

    cairosvg.svg2png(url=svg_file_path, write_to=png_file_path)
if __name__ == '__main__':
    import chess
    asyncio.run(_refrtopng(chess.Board(), 123))