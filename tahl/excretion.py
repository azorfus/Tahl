import torch

def move_to_index(from_sq, to_sq, promotion=None):
    ff, fr = from_sq % 8, from_sq // 8
    tf, tr = to_sq % 8, to_sq // 8
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

# This function finds the moves made in the bitboards by
# taking their respective plane differences and checking for
# displacements in them
def fetch_move(from_board, to_board):
    # fbunwound -> from_board_unwound, tbunwound -> to_board_unwound
    fbunwound = torch.unbind(from_board, dim=0)
    tbunwound = torch.unbind(to_board, dim=0)
    identifiers = []

    # This gets appended with the strings: "castling, white", "castling, black",
    #  "enpassant", "pawn promotion" or remains None depending on the move that's happening
    specialinfo = None

    for i in range(0, 28):
        # tensor.any() returns True if the tensor has any value that's not 0
        # it returns False if the tensor is zeroed out
        if (fbunwound[i] - tbunwound[i]).any():
            identifiers.append(i)

    # identifiers are basically the plane numbers where changes have happened
    # if a piece moved then that corresponding plane number would be an identifier
    # if a piece captured another piece then the numbers of the two corresponding planes
    # would be identifiers 
    for i in identifiers:
        if i < 12:
            diff = tbunwound[i] - fbunwound[i]
            # if a piece is moved then the "to" square would be -1 since we're
            # subtracting 0 (old square) with the 1 (new square)
            from_y, from_x = torch.where(diff == -1)
            # Also if a piece is captured then the "to" coordinates would
            # just be 0, since no piece has moved into them on that corresponding plane
            to_y, to_x = torch.where(diff == 1)
        elif i in [12, 13, 14, 15]:
            # white castling
            specialinfo = "castling, white"
        elif i in [16, 17, 18, 19]:
            # black castling
            specialinfo = "castling, black"
        elif i in [20, 22]:
            # Note to self: Check if we really do need enpassant origin planes
            # en-passant
            specialinfo = "enpassant"

    from_sq = (from_x, from_y)
    to_sq = (to_x, to_y)

    return from_sq, to_sq

def coordtotensor(coords, specialinfo):
    

from misc import *
def mimic_output(fdtensor, pgn_array):
    # We split the massive 4d tensors into a python list of 3d tensors (bitboards)
    # for the convenient processing of each of them into their corresponding Y tensors
    tdtensor = torch.unbind(fdtensor, dim=0)
    i = 0
    while True:
        values = fetch_move(tdtensor[i], tdtensor[i + 1])
        print(values)
        i = i + 1
        if i + 1 >= len(tdtensor):
            break
        if i >= 25:
            break


    
if __name__ == "__main__":
    mimic_output