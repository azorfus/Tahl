import sys

from ingestion import *
from nnet import *

input_dim = 28*8*8
output_dim = 64*73

def move_map(movestr):
    
def move_to_index(from_sq, to_sq, promotion=None):
    def coords(sq):
        return sq % 8, sq // 8

    ff, fr = coords(from_sq)
    tf, tr = coords(to_sq)
    df, dr = tf - ff, tr - fr

    knight_moves = [(1,2),(2,1),(2,-1),(1,-2),(-1,-2),(-2,-1),(-2,1),(-1,2)]
    directions = [(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1)]

    if (df, dr) in knight_moves:
        plane = 56 + knight_moves.index((df, dr))
    elif promotion in ('n', 'b', 'r'):
        push_type = {0: 0, -1: 1, 1: 2}[df]
        promo_piece = {'n': 0, 'b': 1, 'r': 2}[promotion]
        plane = 64 + push_type * 3 + promo_piece
    else:
        dist = max(abs(df), abs(dr))
        unit = (df // dist, dr // dist)
        direction = directions.index(unit)
        plane = direction * 7 + (dist - 1)

    return from_sq * 73 + plane

# Main pipeline 
def pipeline():
    if len(sys.argv) <= 1:
        print("[!] Expected file name!")
        return

    if sys.argv[1] == 'F':
        F = sys.argv[2]
        pgn_data = PGNMatter(F, True)
    else:
        F = sys.argv[1]
        pgn_data = PGNMatter(F, False)
    
	# DATA CONVERSION
    conv_data = alms(pgn_data)

    Y = torch.tensor()

    # NEURAL NETWORK TRAINING
    brain = FFNN(input_dim, output_dim, [14*8*8, 64*28, 64*56])

    # need to write a mapping function for input to output format



if __name__ == "__main__":
	# pipeline()
    move_map("")