import math, random

from sympy import evaluate, mod_inverse
from chess_functions import *
from evaluation import evaluatePosition
import time

turn = 0
asset_directory = 'Chess/assets/'
kingPos = [-1, -1]

enpassant_target = '-'
en_passant = -1
en_passant_turn = -1
halfmove_clock = 0
fullmove = 0

class Piece:
    def __init__(self, team, type, image):
        self.team = team
        self.type = type
        self.image = asset_directory + image
           
# 0 for black, 1 for white
bp = Piece(0, 'p', 'pawn_b.png')
wp = Piece(1, 'p', 'pawn_w.png')
bb = Piece(0, 'b', 'bishop_b.png')
wb = Piece(1, 'b', 'bishop_w.png')
bn = Piece(0, 'n', 'knight_b.png')
wn = Piece(1, 'n', 'knight_w.png')
br = Piece(0, 'r', 'rook_b.png')
wr = Piece(1, 'r', 'rook_w.png')
bq = Piece(0, 'q', 'queen_b.png')
wq = Piece(1, 'q', 'queen_w.png')
bk = Piece(0, 'k', 'king_b.png')
wk = Piece(1, 'k', 'king_w.png')

piece_dict = {
    'P':wp,
    'B':wb,
    'N':wn,
    'R':wr,
    'Q':wq,
    'K':wk,
    'p':bp,
    'b':bb,
    'n':bn,
    'r':br,
    'q':bq,
    'k':bk,
}

castle = {'K':0, 'Q':0, 'k': 0, 'q':0}

def fenToBoard(fen):

    global turn, halfmove_clock, fullmove
    global castle
    global kingPos
    global enpassant_target, en_passant, en_passant_turn

    parts = fen.split(' ')
    pieces_state = parts[0]

    if parts[1] == 'w':
        turn = 1
    else:
        turn = 0

    for char in parts[2]:
        castle[char] = 1

    enpassant_target = parts[3]
    
    file_list = 'abcdefgh'

    if enpassant_target != '-':
        en_passant = getPos(int(enpassant_target[1]), file_list.index(enpassant_target[0]))
        en_passant_turn = turn
    else:
        en_passant_turn = -1
        en_passant = -1

    pos = 0
    fenboard = [' ' for i in range(64)]

    board_state = pieces_state.split('/')
    board_state.reverse()

    halfmove_clock = int(parts[4])

    fullmove = int(parts[5])
    
    for rank in board_state:
        for char in rank:
            if char.isdigit():
                pos += int(char)
            elif char != '/':
                fenboard[pos] = piece_dict[char]

                if piece_dict[char].type == 'k':
                    kingPos[piece_dict[char].team] = pos

                pos += 1

    return fenboard

def PMoves(pos, board): # Returns all possible moves for a pawn, bit sketch, only one that also return capture squares (excluding enpassants)
    possible_moves = []
    capture_moves = []
    
    piece = board[pos]
    rank, file = posToRankFile(pos)

    if piece.team:
        if pos+8 < 64 and board[pos+8] == ' ':
            possible_moves.append(pos+8)
        if pos+9 < 64 and board[pos+9] != ' ' and file != 7:
            if board[pos+9].team == 0:
                possible_moves.append(pos+9)
            capture_moves.append(pos+9)
        if pos+7 < 64 and board[pos+7] != ' ' and file != 0:
            if board[pos+7].team == 0:
                possible_moves.append(pos+7)
            capture_moves.append(pos+7)
        if math.floor(pos/8) == 1 and board[pos + 8] == ' ':
            possible_moves.append(pos+16)

    elif not piece.team:
        if pos-8 > 0 and board[pos-8] == ' ':
            possible_moves.append(pos-8)
        if pos-9 >0 and board[pos-9] != ' ' and file != 0:
            if board[pos-9].team == 1: 
                possible_moves.append(pos-9)
            capture_moves.append(pos-9)
        if pos-7 > 0 and board[pos-7] != ' ' and file != 7:
            if board[pos-7].team == 1:
                possible_moves.append(pos-7)
            capture_moves.append(pos-7)
        if math.floor(pos/8) == 6 and board[pos - 8] == ' ':
            possible_moves.append(pos-16)

    global en_passant
    if en_passant == pos + 1:
        if piece.team:
            possible_moves.append(pos + 9)
        elif not piece.team:
            possible_moves.append(pos - 7)
    elif en_passant == pos - 1:
        if piece.team:
            possible_moves.append(pos + 7)
        elif not piece.team:
            possible_moves.append(pos - 9)
    return possible_moves, capture_moves

def doCastle(type, board):
    global castle
    if type == 6:
        board[5] = wr
        board[7] = ' '
        castle['K'] = False
        castle['Q'] = False
        castle['k'] = False
        castle['q'] = False

    elif type == 2:
        board[3] = wr
        board[0] = ' '
        castle['K'] = False
        castle['Q'] = False
        castle['k'] = False
        castle['q'] = False

    elif type == 62:
        board[61] = br
        board[63] = ' '
        castle['K'] = False
        castle['Q'] = False
        castle['k'] = False
        castle['q'] = False

    elif type == 58:
        board[59] = br
        board[56] = ' '
        castle['K'] = False
        castle['Q'] = False
        castle['k'] = False
        castle['q'] = False

def removeCastle(type, clicked_space): # Turn castle vars to false
    global castle
    if type == 'k':
        if clicked_space == 4:
            castle['K'] = False
            castle['Q'] = False
        elif clicked_space == 60:
            castle['k'] = False
            castle['q'] = False
    elif type == 'r':
        if clicked_space == 0:
            castle['Q'] = False
        elif clicked_space == 7:
            castle['K'] = False
        elif clicked_space == 56:
            castle['q'] = False
        elif clicked_space == 63:
            castle['k'] = False

from brain import treeSearch

def getMove(fen):
    board = fenToBoard(fen)
    # Replace with move generation where move[1] is the move and move[0] is the original position
    # of the piece that moves, i.e. piece at position 1 moves to position 0

    # move, score = treeSearch(turn, 10000000, 3, board)
    move = [0, 0]

    start = time.time()
    for i in range(10000):
        moves = inCheck(board)
    end = time.time()
    print(end - start)


    return move[1], move[0], board

def doMove(fen):
    move, pos, board = getMove(fen)
    file_list = 'abcdefgh'

    global enpassant_target, halfmove_clock, fullmove, castle, en_passant, en_passant_turn

    if board[pos].type == 'k':
        kingPos[turn] = move
        if move == pos + 2 or move == pos - 2:
            doCastle(move, board)
        else:
            removeCastle('k', pos)

    if en_passant != -1 and en_passant_turn == turn:
        en_passant = -1
        en_passant_turn = -1

    if board[pos].type == 'p':
        halfmove_clock = 0
        if (move == pos + 16 and turn) or (move == pos - 16 and not turn):
            en_passant = move
            en_passant_turn = turn
            
            rank, file = posToRankFile(en_passant)

            if turn:
                enpassant_target = file_list[file] + str(rank)
            else:
                enpassant_target = file_list[file] + str(rank + 2)

    if board[pos].type == 'r':
        removeCastle('r', pos)
    
    if board[pos].type == 'p' and turn != en_passant_turn:
        if turn and move == en_passant + 8:
            board[en_passant] = ' '
        elif not turn and move == en_passant - 8:
            board[en_passant] = ' '
    
    if board[move] != ' ':
        halfmove_clock = 0

    board[move] = board[pos]
    board[pos] = ' '

    if turn == 0:
        fullmove += 1

    enpassant_target = '-'
    halfmove_clock += 1  

    state = getFEN(not turn, castle, enpassant_target, halfmove_clock, fullmove, board)

    return board, state
