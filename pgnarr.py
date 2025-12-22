import io
import sys
import chess
import chess.pgn
import numpy as np

board_map = {
    "a1": (0, 0), "a2": (0, 1), "a3": (0, 2), "a4": (0, 3),
    "a5": (0, 4), "a6": (0, 5), "a7": (0, 6), "a8": (0, 7),
    "b1": (1, 0), "b2": (1, 1), "b3": (1, 2), "b4": (1, 3),
    "b5": (1, 4), "b6": (1, 5), "b7": (1, 6), "b8": (1, 7),
    "c1": (2, 0), "c2": (2, 1), "c3": (2, 2), "c4": (2, 3),
    "c5": (2, 4), "c6": (2, 5), "c7": (2, 6), "c8": (2, 7),
    "d1": (3, 0), "d2": (3, 1), "d3": (3, 2), "d4": (3, 3),
    "d5": (3, 4), "d6": (3, 5), "d7": (3, 6), "d8": (3, 7),
    "e1": (4, 0), "e2": (4, 1), "e3": (4, 2), "e4": (4, 3),
    "e5": (4, 4), "e6": (4, 5), "e7": (4, 6), "e8": (4, 7),
    "f1": (5, 0), "f2": (5, 1), "f3": (5, 2), "f4": (5, 3),
    "f5": (5, 4), "f6": (5, 5), "f7": (5, 6), "f8": (5, 7),
    "g1": (6, 0), "g2": (6, 1), "g3": (6, 2), "g4": (6, 3),
    "g5": (6, 4), "g6": (6, 5), "g7": (6, 6), "g8": (6, 7),
    "h1": (7, 0), "h2": (7, 1), "h3": (7, 2), "h4": (7, 3),
    "h5": (7, 4), "h6": (7, 5), "h7": (7, 6), "h8": (7, 7),
}

numpy_init_bitboard = np.zeros((28, 8, 8), dtype=np.int8)

def check_empty_squares(board, *args):
    
    square_status_array = []
    
    for str_square in args:
        square = chess.parse_square(str_square)
        square_status = (board.piece_at(square) is None)
        square_status_array.append(square_status)

    return all(square_status_array)

# DEBUG FUNCTION
def print_castling_status(gs):
    print(
        "\n=== CASTLING STATUS ===\n"
        f"WHITE  | King-side  | right: {gs['white_ks_cright']} | available: {gs['white_ks_cavail']}\n"
        f"       | Queen-side | right: {gs['white_qs_cright']} | available: {gs['white_qs_cavail']}\n"
        "\n"
        f"BLACK  | King-side  | right: {gs['black_ks_cright']} | available: {gs['black_ks_cavail']}\n"
        f"       | Queen-side | right: {gs['black_qs_cright']} | available: {gs['black_qs_cavail']}\n"
        "========================\n"
    )

def process_pgn(pgn_data_array):

    piece_types = [chess.PAWN, chess.ROOK, chess.KNIGHT,
                   chess.BISHOP, chess.KING, chess.QUEEN]
    
    for each_pgn in pgn_data_array:

        game = chess.pgn.read_game(io.StringIO(each_pgn))
        board = game.board()

        for move in game.mainline_moves():
            
            # DEBUG 
            game_status = {
                "white_ks_cright": False,
                "white_ks_cavail": False,
                
                "white_qs_cright": False,
                "white_qs_cavail": False,

                "black_ks_cright": False,
                "black_ks_cavail": False,

                "black_qs_cright": False,
                "black_qs_cavail": False
            }
            
            bitboard = np.zeros((28, 8, 8), dtype=np.int8)
            
            # First six slices are for white piece info in order of pawn, rook, knight, bishop, king and queen
            # Next six slices act as the black piece info in the same order.
            for i in range(len(piece_types)):
                for sq in board.pieces(piece_types[i], chess.WHITE):
                    bitboard[i][sq // 8][sq % 8] = 1

                for sq in board.pieces(piece_types[i], chess.BLACK):
                    bitboard[i + 6][sq // 8][sq % 8] = 1

            # Update castling information

            # *** WHITE ***

            # White king's side
            if bool(board.castling_rights & chess.BB_H1): # White can castle with a1 rook
                # Slice 12 and 13 are for white castling rights with the king's side and castling possibility with the a1 rook
                bitboard[12] = np.ones((8, 8), dtype=np.int8)

                game_status["white_ks_cright"] = True

            if bool(board.castling_rights & chess.BB_H1) and check_empty_squares(board, "f1", "g1"):
                bitboard[13] = np.ones((8, 8), dtype=np.int8)

                game_status["white_ks_cavail"] = True
            
            # White queen's side
            if bool(board.castling_rights & chess.BB_A1): # White can castle with h1 rook
                # Slice 14 and 15 are for white castling rights with the queen's and castling possibility with the h1 rook
                bitboard[14] = np.ones((8, 8), dtype=np.int8)

                game_status["white_qs_cright"] = True

            if bool(board.castling_rights & chess.BB_A1) and check_empty_squares(board, "b1", "c1", "d1"):
                bitboard[13] = np.ones((8, 8), dtype=np.int8)

                game_status["white_qs_cavail"] = True

            # *** BLACK ***

            # Black king's side
            if bool(board.castling_rights & chess.BB_H8): # Black can castle with h8 rook
                # Slice 16 and 17 are for black's castling rights with the king's side and castling possibility with the h8 rook
                bitboard[16] = np.ones((8, 8), dtype=np.int8)

                game_status["black_ks_cright"] = True

            if bool(board.castling_rights & chess.BB_H8) and check_empty_squares(board, "f8", "g8"):
                bitboard[17] = np.ones((8, 8), dtype=np.int8)

                game_status["black_ks_cavail"] = True

            # Black queen's side
            if bool(board.castling_rights & chess.BB_A8): # Black can castle with a8 rook
                # Slice 18 and 19 are for black's castling rights with the queen's side and castling possibility with the h8 rook
                bitboard[18] = np.ones((8, 8), dtype=np.int8)

                game_status["black_qs_cright"] = True

            if bool(board.castling_rights & chess.BB_A8) and check_empty_squares(board, "b8", "c8", "d8"):
                bitboard[19] = np.ones((8, 8), dtype=np.int8)

                game_status["black_qs_cavail"] = True

            print(board)
            print_castling_status(game_status)

            board.push(move)
'''
            for z in bitboard:
                for y in z:
                    for x in y:
                        print(x, end=" ")
                    print()
                print()
                
            break
'''


def flush_pgn(output_file, pgn_bit_slices):
    pass

def main():
    if len(sys.argv) <= 1:
        print("[!] Expected file name!")
        return
    
    filename = sys.argv[1]
    output_file = "output.arr"

    if len(sys.argv) <= 2:
        print("[*] Output file name not provided. Defaulted to output.arr")
    else:
        output_file = sys.argv[2]

    print(f"[*] Parsing {filename} and outputting to {output_file}")

    with open(filename, 'r') as source:
        pgn_limit = 1000
        pgn_count = 0
        pgn_data_array = []
        while pgn_count <= pgn_limit:
            line = source.readline()
            
            if line[0] == '1':
                pgn_data_array.append(line)
                pgn_count += 1
            else:
                continue

            if pgn_count == pgn_limit:
                print(f"[*] Buffer pgn Load limit reached ({pgn_count})")
                print(f"[*] Flushing and processing the loaded pgn Data...")
                pgn_bit_slices = process_pgn(pgn_data_array)
                pgn_data_array.clear()
                flush_pgn(output_file, pgn_bit_slices)
                # pgn_bit_slices.clear()


if __name__ == "__main__":
    main()