import chess
import chess.engine
import chess.svg
import cairosvg


async def svg_to_png(board, user) -> None:
    with open(f'../chess_board_screen/{user}.svg', 'w') as file:
        file.write(chess.svg.board(board, size=1000))

    svg_file_path = f"../chess_board_screen/{user}.svg"

    png_file_path = f"../chess_board_screen/{user}.png"

    cairosvg.svg2png(url=svg_file_path, write_to=png_file_path)
