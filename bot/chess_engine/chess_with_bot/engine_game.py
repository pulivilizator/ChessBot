import asyncio
import chess
import chess.engine
import chess.svg
import aspose.words as aw
from interface import keyboards

engine = chess.engine.SimpleEngine.popen_uci(r"..\stockfish\stockfish.exe")
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

    fileName = f"../chess_board_screen/{user}.svg"
    doc = aw.Document()

    builder = aw.DocumentBuilder(doc)

    shape = builder.insert_image(fileName)

    pageSetup = builder.page_setup
    pageSetup.page_width = shape.width
    pageSetup.page_height = shape.height
    pageSetup.top_margin = 0
    pageSetup.left_margin = 0
    pageSetup.bottom_margin = 0
    pageSetup.right_margin = 0

    doc.save(f"../chess_board_screen/{user}.png")

if __name__ == '__main__':
    import chess
    asyncio.run(_refrtopng(chess.Board(), 123))