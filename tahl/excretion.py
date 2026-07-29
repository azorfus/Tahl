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

def fetch_move(bitboard, move, color):
    piece_type = ""
    to_sq = ""
    from_sq = ()

    # CONVERTING THE LAYERED BITBOARD DESIGN INTO AN ARRAY OF BITBOARD LAYERS
    unwoundboard = torch.unbind(bitboard, dim=0)

    if move[0] in "KQBNR":
        piece_type = move[0]
        to_sq = move[1:]
    else:
        piece_type = "P"
        to_sq = move
    
    if piece_type == "K":
        if color == "white":
            y, x = torch.where(unwoundboard[4] == 1)
            from_sq = (x.item(), y.item())
    else if piece_type == "Q":
        if color == "white":
            y, x = torch.where(unwoundboard[5] == 1)
            from_sq = (x.item(), y.item())
    else if piece_type == "K":
        if color == "black":
            y, x = torch.where(unwoundboard[10] == 1)
            from_sq = (x.item(), y.item())
    else if piece_type == "Q":
        if color == "black":
            y, x = torch.where(unwoundboard[11] == 1)
            from_sq = (x.item(), y.item())

    # PROCESSING to_sq
    to_sq_int = (int(ord(to_sq[0] - 97)), int(to_sq[1]) - 1)

    return from_sq, to_sq_int

    

from misc import print_bitboards
def mimic_output(fdtensor, pgn_array):
    # We split the massive 4d tensors into a python list of 3d tensors (bitboards)
    # for the convenient processing of each of them into their corresponding Y tensors
    tdtensor = torch.unbind(fdtensor, dim=0)
    fetch_move(tdtensor[0], "Ke3", "white")


    
if __name__ == "__main__":
    mimic_output