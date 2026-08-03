import io
import os
import sys
import chess
import chess.pgn
import numpy as np

import torch

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

# How the bitboard input is sliced and designed:
# First 12 slices are for piece information

# White pawn placement, White rook, knight, bishop, king and queen (6)

# The next 6 are for black in the same order (12)

# The next 4 are white castling status slices (16)
# The next 4 are black castling status slices (20)

# The next four are for enpassant information (24)
# First two for white: one for enpassant squares, the next for direction
# The next two follow the same order but for black

# Last 4 slices are for buffered storage of previous positions (28)

#    ---------------------------------------------------------
#    This is the start of the code block that does the pgn parsing
#    ---------------------------------------------------------

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

# You feed the function an array of pgn strings and it converts it to Tahl's custom input format
# (as pgn bitboards) which then later needs to be converted into torch tensors for training Tahl's neural nets
# PGN BITBOARD -> NUMPY ARRAY of size 28x8x8, datatype = float32
# why 32 bit float for 0s and 1s? because easier to convert to float tensors in torch since
# neural nets need float inputs for calculation (weights and biases are floats bruh)
def process_pgn(pgn_data_array):

    piece_types = [chess.PAWN, chess.ROOK, chess.KNIGHT,
                   chess.BISHOP, chess.KING, chess.QUEEN]

    pgn_bitboards = []
    
    for each_pgn in pgn_data_array:
        game = chess.pgn.read_game(io.StringIO(each_pgn))
        assert(game is not None)

        board = game.board()

        for move in game.mainline_moves():
            
            bitboard = np.zeros((28, 8, 8), dtype=np.float32)

            if board.turn == chess.WHITE:
                bitboard[24] = np.zeros((8, 8), dtype=np.float32)
            else:
                bitboard[24] = np.ones((8, 8), dtype=np.float32)

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
            
            # *************************************************
            # !!! THIS IS THE CODE THAT UPDATES PIECE POSITIONS
            # *************************************************
            # First six slices are for white piece info in order of pawn, rook, knight, bishop, king and queen
            # Next six slices act as the black piece info in the same order.
            for i in range(len(piece_types)):
                for sq in board.pieces(piece_types[i], chess.WHITE):
                    bitboard[i][sq % 8][sq // 8] = 1

                for sq in board.pieces(piece_types[i], chess.BLACK):
                    bitboard[i + 6][sq % 8][sq // 8] = 1

            # Update castling information

            # *** WHITE ***

            # White king's side
            if board.has_kingside_castling_rights(chess.WHITE): 
                bitboard[12] = np.ones((8, 8), dtype=np.float32)

                game_status["white_ks_cright"] = True

            if chess.Move.from_uci("e1g1") in board.legal_moves:
                bitboard[13] = np.ones((8, 8), dtype=np.float32)

                game_status["white_ks_cavail"] = True
            
            # White queen's side
            if board.has_queenside_castling_rights(chess.WHITE): 
                bitboard[14] = np.ones((8, 8), dtype=np.float32)

                game_status["white_qs_cright"] = True

            if chess.Move.from_uci("e1c1") in board.legal_moves:
                bitboard[15] = np.ones((8, 8), dtype=np.float32)

                game_status["white_qs_cavail"] = True

            # *** BLACK ***

            # Black king's side
            if board.has_kingside_castling_rights(chess.BLACK): 
                bitboard[16] = np.ones((8, 8), dtype=np.float32)

                game_status["black_ks_cright"] = True

            if chess.Move.from_uci("e8g8") in board.legal_moves:
                bitboard[17] = np.ones((8, 8), dtype=np.float32)

                game_status["black_ks_cavail"] = True

            # Black queen's side
            if board.has_queenside_castling_rights(chess.BLACK): 
                bitboard[18] = np.ones((8, 8), dtype=np.float32)

                game_status["black_qs_cright"] = True

            if chess.Move.from_uci("e8c8") in board.legal_moves:
                bitboard[19] = np.ones((8, 8), dtype=np.float32)

                game_status["black_qs_cavail"] = True

            # Checking and updating en passant status slices
            if board.has_legal_en_passant():
                ep_square = board.ep_square
                assert(ep_square is not None)

                # target en passant square marking
                if board.turn == chess.WHITE:
                    bitboard[20][ep_square % 8][ep_square // 8] = 1
                elif board.turn == chess.BLACK:
                    bitboard[22][ep_square % 8][ep_square // 8] = 1

                # origin of en passant
                for lmove in board.legal_moves:
                    if lmove.to_square == ep_square:
                        if board.turn == chess.WHITE:
                            bitboard[21][lmove.from_square % 8][lmove.from_square // 8] = 1
                        elif board.turn == chess.BLACK:
                            bitboard[23][lmove.from_square % 8][lmove.from_square // 8] = 1

            board.push(move)
            pgn_bitboards.append(bitboard)

    return pgn_bitboards

#    ---------------------------------------------------------
#    This is the end of the code block that does the pgn parsing
#    ---------------------------------------------------------

# Essentially we are passing around a data input file along with it's pointer, which
# basically points to the last pgn game accessed. I thought it'd be a good idea to put them
# together in a single object along with their methods. Probably more clean and efficient (?)
class PGNMatter:
    # we'll be essentially reading folders with game data
    # this class makes it very easy to access all the data, you essentially just keep reading
    # and the class abstracts all the backend work done to switch files and keep track of the
    # data that's being read
    files = []
    input_stream = "" # initial path given by user
    file_name = "" # points to the current file
    file_pointer = 0 # points to the current file index
    is_folder = False
    
    pgn_pointer = 0

    # Parameters: File/Folder Name, True if folder, precounted position of pgn if needed
    def __init__(self, input_stream, folder = False, pgn_pointer = 0):
        self.input_stream = input_stream
        self.file_name = input_stream
        self.is_folder = folder
        
        if folder == False:
            try:
                self.file_pointer = open(self.file_name, 'r', encoding="utf-8")
            except Exception as e:
                print("Error: Can't read input file, setting base paramenters to NULL. Reinitialize!")
                print("[Python Error]:", e)

            self.pgn_pointer = pgn_pointer
        else:
            for filename in os.listdir(self.input_stream):
                if self.input_stream[len(input_stream) - 1] != "/":
                    self.input_stream = self.input_stream + "/"
                self.files.append(self.input_stream + filename)
            
            self.file_name = self.files[self.file_pointer]
            try:
                self.file_pointer = open(self.file_name, 'r', encoding="utf-8")
            except Exception as e:
                print("Error: Can't read input file, setting base paramenters to NULL. Reinitialize!")
                print("[Python Error]:", e)
            self.pgn_count = 0


    def read(self, quantity = 1024):
        if self.file_pointer.closed:
            print("Error: File pointer closed! What are you reading?")
            return 0

        pgn_count = 0
        return_buffer = []
        while pgn_count < quantity:
            line = self.file_pointer.readline()

            if self.is_folder and line == '':
                self.file_pointer += 1
                if self.file_pointer < len(files):
                    self.file_pointer.close()
                    self.file_name = files[file_pointer]
                    self.file_pointer = open(file_name, 'r', encoding="utf-8")
                    print(f"Data file ended. Shifting to next file!!! (Next file: {file_name})")
                    self.pgn_pointer = 0
                else:
                    break

            # I'm basically building this to extract only the move lines, and they always start with
            # 1. cause they're all game moves and start with the 1st move :P
            # I'm ignoring the game information for now
            if line[0] == '1':
                return_buffer.append(line)
                pgn_count += 1

        self.pgn_pointer += quantity
        return return_buffer

    def conv_to_torchtensor(self, bitboards):
        converted_bitboards = []
        for board in bitboards:
            converted_board = torch.from_numpy(board)
            converted_bitboards.append(converted_board)
        return converted_bitboards

        
'''
    def __del__(self):
        # ensuring that the underlying system stream closes safely when the object is destroyed
        if hasattr(self, 'file_pointer') and not self.file_pointer.closed:
            self.file_pointer.close()
'''
def pgn_to_movelist(pgn_data):
    massive_array = []
    for element in pgn_data:
        pgn_array = element.split(' ')
        pgn_array_2 = []
        for i in pgn_array:
            if i[0] not in "123456789":
                pgn_array_2.append(i)
        # EACH GAME HAS ITS OWN ARRAY, this makes it easier for us to know
        # when the game starts and ends.
        massive_array.append(pgn_array_2)
    return massive_array

def alms(pgn_data, quantity = 1024):
    raw_data = pgn_data.read(quantity)
    pgn_array = pgn_to_movelist(raw_data)
    pgn_bitboards = process_pgn(raw_data)
    tensor_data = pgn_data.conv_to_torchtensor(pgn_bitboards)
    one_big_tensor = torch.stack(tensor_data, dim=0)
    return one_big_tensor, pgn_array
    

def main():
    if len(sys.argv) <= 1:
        print("Expected file name!")
        return
    
    folder = sys.argv[1]
    
    pgn_data = PGNMatter(folder, True)
    conv_data = alms(pgn_data)
    print(conv_data[0].size())

if __name__ == "__main__":
    main()
