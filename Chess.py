from cv2 import getOptimalDFTSize
import pygame as pg
import math
from sys import exit
import random
from requests import get
from random import choice
import stockfish as sf


asset_directory = 'Chess/assets/'

# Stuff
pg.init()

HEIGHT = 480
WIDTH = 480

screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Chess")

clock = pg.time.Clock()

# Graphics
background = pg.image.load("Chess/assets/board1.jpg").convert()
background = pg.transform.scale(background, (WIDTH, HEIGHT))

PIECE_HIGHLIGHT = (252, 185, 234)
MOVES_HIGHLIGHT = (210, 210, 210) # The circle thingy
LEGAL_CAPTURE_HIGHLIGHT = (245, 158, 184)
LIGHT_SQUARE_COLOR = (233, 233, 233)
DARK_SQUARE_COLOR = (87, 144, 193)
PROMO_COLOR = (252, 185, 234)

WHITE = 0
BLACK = 1

PIECE_TYPES = {
    'p':1,
    'n':2,
    'b':3,
    'r':4,
    'q':5,
    'k':6
}

PIECE_NAMES = {
    1:'p',
    2:'n',
    3:'b',
    4:'r',
    5:'q',
    6:'k'
}

TEAM_VALUES = {
    'w':0,
    'b':8
}

IMAGE_DIRECTORY = {
    1:'pawn_w.png',
    2:'knight_w.png',
    3:'bishop_w.png',
    4:'rook_w.png',
    5:'queen_w.png',
    6:'king_w.png',
    9:'pawn_b.png',
    10:'knight_b.png',
    11:'bishop_b.png',
    12:'rook_b.png',
    13:'queen_b.png',
    14:'king_b.png'
}

board = [0] * 64
pieces = []
white_pieces = []
black_pieces = []

white_threats = []
black_threats = []

pinned_pieces = [0] * 64

possible_moves = []
white_check_pieces = []
black_check_pieces = []

enp_target = -1
castles = {'K':0, 'Q':0, 'k':0, 'q':0}
turn = WHITE
halfmove = 0
fullmove = 0

potential_moves = [0] * 64
promotion = 0

# Graphics
def displayBackground(): # Displays the background
    light = True

    for i in range(64):
        x, y = posToXY(i)

        if i % 8 == 0:
            light = not light

        if light:
            rectangle = (x, y, 60, 60)
            screen.fill(LIGHT_SQUARE_COLOR, rect=rectangle)

        else:
            rectangle = (x, y, 60, 60)
            screen.fill(DARK_SQUARE_COLOR, rect=rectangle)

        light = not light

def displayPieces():
    for i in pieces:
        location = asset_directory + IMAGE_DIRECTORY[board[i]]
        x, y = posToXY(i)

        image = pg.image.load(location)
        screen.blit(image, (x,y))

def displayHighlight(pos):
    x, y= posToXY(pos)
    rectangle = (x, y, 60, 60)
    screen.fill(PIECE_HIGHLIGHT, rectangle)

def displayMoves(moves):
    for move in moves:
        x,y = posToXY(move)

        if board[move] == 0:
            pg.draw.circle(screen, MOVES_HIGHLIGHT, (x + 30, y + 30), 5)
        else:
            rectangle = (x, y, 60, 60)
            screen.fill(LEGAL_CAPTURE_HIGHLIGHT, rectangle)





# Conversions
def RFtoXY(rank, file): # Turn a set of coordinates from 1-8 to 0-400
    return (file) * 60, 420 - (rank) * 60

def XYtoRankFile(x,y): # Opposite of toXY
    return 7 - math.floor(y/60), math.floor(x/60)

def posToXY(pos): # The name
    rank, file = posToRF(pos)
    return RFtoXY(rank, file)

def XYToPos(x, y): # The name
    rank, file = XYtoRankFile(x, y)
    return(RFToPos(rank, file))

def posToRF(pos): # Gets the rank and file from a number 0-63
    rank = math.floor(pos/8)
    file = pos % 8

    return rank, file

def RFToPos(rank, file): # Returns a number 0-63 from rank,file
    return (rank * 8) + file

def getValue(piece):
    return TEAM_VALUES[piece[0]] + PIECE_TYPES[piece[1]]

def spaceToPos(space):
    files = 'abcdefgh'
    file = files.index(space[0])
    rank = int(space[1]) - 1

    return RFToPos(rank, file)

def getFEN():
    rString = ''
    count = 0

    for rank in range(7, -1, -1):
        for file in range(8):
            if board[RFToPos(rank, file)] == 0:
                count += 1
            else:
                if count > 0:
                    rString += str(count)
                    count = 0
                
                piece = board[RFToPos(rank,file)]
                if piece // 8 == WHITE:
                    rString += PIECE_NAMES[piece].upper
                else:
                    rString += PIECE_NAMES[piece%8]

        if count > 0:
            rString += str(count)
            count = 0

        if rank != 0:
            rString += '/'

    rString += ' '

    if turn == WHITE: rString += 'w'
    else: rString += 'b'

    rString += ' '
    c = 'KQkq'

    for a in c:
        if castles[a] == 1: rString += a




# Basic
def getTeam(piece):
    return piece // 8

def getType(piece):
    return piece % 8

def getRank(pos):
    return pos // 8

def getFile(pos):
    return pos % 8

def getKingPos(team):
    if (team == WHITE):
        for space in pieces:
            if board[space] == 6:
                return space
    else:
        for space in pieces:
            if board[space] == 14:
                return space
    
    return -1

def noneBetween(s1, s2):
    a = max(s1, s2)
    b = min(s1, s2)

    if getFile(a) == getFile(b):
        i = a+8
        while i < 64:
            if (i==b):
                return True
            elif (board[i] != 0):
                return False
            i+=8
    elif getRank(a) == getRank(b):
        i = a+1
        while i%8 != 0:
            if (i==b):
                return True
            elif (board[i] != 0):
                return False
            i+=1
    elif a%9 == b%9:
        i = a+9
        while i < 64 and i%8 != 0:
            if (i==b):
                return True
            elif (board[i] != 0):
                return False
            i+=9
    elif a%7 == b%7:
        i = a+7
        while i < 64 and i%8 != 7:
            if (i==b):
                return True
            elif (board[i] != 0):
                return False
            i+=7
    return False

# Move generation
def pawnMoves(team, pos):
    global white_threats, black_threats, white_check_pieces, black_check_pieces
    moves = []

    rank = getRank(pos)
    file = getFile(pos)

    if team == WHITE:
        if pos+8 not in pieces:
            moves.append(pos+8)
            if rank == 1 and pos+16 not in pieces:
                moves.append(pos+16)
        if file == 0:
            white_threats.append(pos+9)
            if pos+9 in black_pieces:
                moves.append(pos+9)

                if board[pos+9] == 14:
                    white_check_pieces.append(pos)
            elif enp_target == pos+9:
                moves.append(pos+9)
        elif file == 7:
            white_threats.append(pos+7)
            if pos+7 in black_pieces:
                moves.append(pos+7)
                if board[pos+7] == 14:
                    white_check_pieces.append(pos)
            elif enp_target == pos+7:
                moves.append(pos+7)
        else:
            white_threats.append(pos+9)
            if pos+9 in black_pieces:
                moves.append(pos+9)
                if board[pos+9] == 14:
                    white_check_pieces.append(pos)
            elif enp_target == pos+9:
                moves.append(pos+9)

            white_threats.append(pos+7)
            if pos+7 in black_pieces:
                moves.append(pos+7)
                if board[pos+7] == 14:
                    white_check_pieces.append(pos)
            elif enp_target == pos+7:
                moves.append(pos+7)
    
    else:
        if pos-8 not in pieces:
            moves.append(pos-8)
            if rank == 6 and pos-16 not in pieces:
                moves.append(pos-16)
        if file == 7:
            black_threats.append(pos-9)
            if pos-9 in white_pieces:
                moves.append(pos-9)
                if board[pos-9] == 6:
                    black_check_pieces.append(pos)
            elif enp_target == pos-9:
                moves.append(pos-9)
        elif file == 0:
            black_threats.append(pos-7)
            if pos-7 in white_pieces:
                moves.append(pos-7)
                if board[pos-7] == 6:
                    black_check_pieces.append(pos)
            elif enp_target == pos-7:
                moves.append(pos-7)
        else:
            black_threats.append(pos-9)
            if pos-9 in white_pieces:
                moves.append(pos-9)
                if board[pos-9] == 6:
                    black_check_pieces.append(pos)
            elif enp_target == pos-9:
                moves.append(pos-9)

            black_threats.append(pos-7)
            if pos-7 in white_pieces:
                moves.append(pos-7)
                if board[pos-7] == 6:
                    black_check_pieces.append(pos)
            elif enp_target == pos-7:
                moves.append(pos-7)
    return moves

def knightValid(pos, move, team):
    if move < 0 or move >= 64:
        return False
    
    diff = abs(getFile(pos) - getFile(move))

    if diff == 1 or diff == 2:
        if board[move] == 0:
            return True
        elif getTeam(board[move]) != team:

            return True
    
    return False

def knightMoves(team, pos):
    global white_threats, black_threats
    moves = []
    possible_moves = [pos + 10, pos - 10, pos + 6, pos - 6, pos + 15, pos - 15, pos + 17, pos - 17]

    for move in possible_moves:
        if knightValid(pos, move, team):
            moves.append(move)

            if team == WHITE:
                white_threats.append(move)
                if board[move] == 14:
                    global white_check_pieces
                    white_check_pieces.append(pos)
            else:
                black_threats.append(move)
                if board[move] == 6:
                    global black_check_pieces
                    white_check_pieces.append(pos)
    
    return moves

offsets = [[-1, -1, 0], [1, 1, 0], [-8, 0, -1], [8, 0, 1], [-7, 1, -1], [7, -1, 1], [-9, -1, -1], [9, 1, 1]]

def bishopMoves(team, pos):
    global white_threats, black_threats
    bsets = offsets[4:]
    kingPos, file, rank = getKingPos(not team), getFile(pos), getRank(pos)
    moves = []
    global pinned_pieces

    for set in bsets:
        f, r = file, rank
        mset, fset, rset = set[0], set[1], set[2]
        i = pos + mset
        f += fset
        r += rset

        while 0<=i<64 and 0<=f<8 and 0<=r<8:
            if team == WHITE:
                white_threats.append(i)
            else:
                black_threats.append(i)
            if board[i] == 0:
                moves.append(i)
            elif getTeam(board[i]) == team:
                break
            elif getTeam(board[i]) != team:
                moves.append(i)
                if noneBetween(i, kingPos):
                    pinned_pieces[i] = pos
                if team == WHITE:
                    white_threats.append(i)
                    if board[i] == 14:
                        global white_check_pieces
                        white_check_pieces.append(pos)
                else:
                    black_threats.append(i)
                    if board[i] == 6:
                        global black_check_pieces
                        black_check_pieces.append(pos)
                break

            f += fset
            r += rset
            i += mset
    return moves

def rookMoves(team, pos):
    bsets = offsets[:4]
    kingPos, file, rank = getKingPos(not team), getFile(pos), getRank(pos)
    moves = []
    global pinned_pieces, white_threats, black_threats

    for set in bsets:
        f, r = file, rank
        mset, fset, rset = set[0], set[1], set[2]
        i = pos + mset
        f += fset
        r += rset

        while 0 <=i<64 and 0<=f<8 and 0<=r<8:
            if team == WHITE:
                white_threats.append(i)
            else:
                black_threats.append(i)
            if board[i] == 0:
                moves.append(i)
            elif getTeam(board[i]) == team:
                break
            elif getTeam(board[i]) != team:
                moves.append(i)
                if noneBetween(i, kingPos):
                    pinned_pieces[i] = pos
                if team == WHITE:
                    white_threats.append(i)
                    if board[i] == 14:
                        global white_check_pieces
                        white_check_pieces.append(pos)
                else:
                    black_threats.append(i)
                    if board[i] == 6:
                        global black_check_pieces
                        black_check_pieces.append(pos)
                break

            f += fset
            r += rset
            i += mset
    return moves

def queenMoves(team, pos):
    bsets = [x for x in offsets]
    kingPos, file, rank = getKingPos(not team), getFile(pos), getRank(pos)
    moves = []
    global pinned_pieces, white_threats, black_threats

    for set in bsets:
        f, r = file, rank
        mset, fset, rset = set[0], set[1], set[2]
        i = pos + mset
        f += fset
        r += rset

        while 0 <=i<64 and 0<=f<8 and 0<=r<8:
            if team == WHITE:
                white_threats.append(i)
            else:
                black_threats.append(i)
            if board[i] == 0:
                moves.append(i)
            elif getTeam(board[i]) == team:
                break
            elif getTeam(board[i]) != team:
                moves.append(i)
                if noneBetween(i, kingPos):
                    pinned_pieces[i] = pos
                if team == WHITE:
                    white_threats.append(i)
                    if board[i] == 14:
                        global white_check_pieces
                        white_check_pieces.append(pos)
                else:
                    black_threats.append(i)
                    if board[i] == 6:
                        global black_check_pieces
                        black_check_pieces.append(pos)  
                break

            f += fset
            r += rset
            i += mset
    return moves

def kingMoves(team, pos):
    global white_threats, black_threats
    possible_moves = [1, -1, 8, -8, 7, -7, 9, -9]
    moves = []

    for offset in possible_moves:
        move = pos + offset

        if move < 64 and move >= 0:
            if abs(getFile(move) - getFile(pos)) == 1:
                if team == WHITE:
                    white_threats.append(move)
                else:
                    black_threats.append(move)

                if board[move] == 0:
                    moves.append(move)
                elif getTeam(board[move]) != team:
                    moves.append(move)
    
    if team == WHITE:
        if castles['K'] and board[5] ==0 and board[6] ==0:
            moves.append(6)
        if castles['Q'] and board[1] ==0 and board[2] ==0 and board[3] ==0:
            moves.append(2)
    else:
        if castles['k'] and board[61] ==0 and board[62] ==0:
            moves.append(62)
        if castles['q'] and board[57] ==0 and board[58] ==0 and board[59] ==0:
            moves.append(58)

    return moves



# Technical stuff
move_dict = {
    1: pawnMoves,
    2: knightMoves,
    3: bishopMoves,
    4: rookMoves,
    5: queenMoves,
    6: kingMoves
}

def updateCastles():
    global castles

    if castles['K'] == 1:
        if board[4] != 6 or board[7] != 4:
            castles['K'] = 0
    if castles['Q'] == 1:
        if board[4] != 6 or board[0] != 4:
            castles['Q'] = 0
    if castles['k'] == 1:
        if board[60] != 14 or board[63] != 12:
            castles['k'] = 0
    if castles['q'] == 1:
        if board[60] != 14 or board[56] != 12:
            castles['q'] = 0

def inCheck(team):
    kingPos = getKingPos(team)

    if team == WHITE:
        if kingPos in black_threats:
            return 1
        else:
            return 0
    else:
        if kingPos in white_threats:
            return 1
        else:
            return 0

def checkLegality(pos, move, incheck=0):
    # No castling through check
    if getType(board[pos]) == 6 and abs(move - pos) == 2:
        for i in range(min(pos,move), max(pos+1,move+1)):
            if getTeam(board[pos]) == WHITE:
                if i in black_threats: return 0
            elif getTeam(board[pos]) == BLACK:
                if i in white_threats: return 0
    
    # Can't move pinned piece
    if pinned_pieces[pos] != 0:
        pinner = pinned_pieces[pos]

        if getFile(pinner) == getFile(pos) and getFile(move) != getFile(pos): return 0
        elif getRank(pinner) == getRank(pos) and getRank(move) != getRank(pos): return 0
        elif pinner % 9 == pos % 9 and move % 9 != pos % 9: return 0
        elif pinner % 7 == pos % 7 and move % 9 != pos % 7: return 0

    # If in check, can only either capture, block, or move king
    if incheck == 1:
        team = getTeam(board[pos])
        
        if team == WHITE:
            check_pieces = [x for x in black_check_pieces]
        else:
            check_pieces = [x for x in white_check_pieces]

        if board[pos]%8 == 6:
            if team == WHITE and move in black_threats: return 0
            elif team == BLACK and move in white_threats: return 0
        else:
            if len(check_pieces) > 1: return 0

            if board[check_pieces[0]]%8 == 3 or board[check_pieces[0]]%8 == 4 or board[check_pieces[0]]%8 == 5:
                kingPos = getKingPos(team)
                
                a,b = min(check_pieces[0], kingPos), max(check_pieces[0], kingPos)

                if getFile(a) == getFile(b) == getFile(move) and a < move < b: return 1
                elif getRank(a) == getRank(b) == getRank(move) and a < move < b: return 1
                elif a%9 == b%9 == move%9 and a < move < b: return 1
                elif a%7 == b%7 == move%7 and a < move < b: return 1
            
            if move == check_pieces[0]: return 1
            else:
                return 0

    return 1

def FENToBoard(fen):
    global turn, enp_target, castles, pieces
    parts = fen.split(' ')

    state = parts[0].split('/')
    state.reverse()
    
    if parts[1] == 'w': turn = WHITE
    else: turn = BLACK

    if parts[2] != '-':
        for c in parts[2]:
            castles[c] = 1

    if parts[3] == '-': enp_target = -1
    else: enp_target = spaceToPos(parts[3])

    fenboard = [0] * 64
    pos = 0

    for rank in state:
        if pos < 64:
            for c in rank:
                if c.isdigit(): pos += int(c)
                else:
                    if c.isupper():
                        fenboard[pos] = PIECE_TYPES[c.lower()]
                        white_pieces.append(pos)
                    else:
                        fenboard[pos] = PIECE_TYPES[c] + 8
                        black_pieces.append(pos)
                    
                    pieces.append(pos)
                    pos+=1
    
    return fenboard

def performMove(pos, move):
    global board, enp_target, pieces

    if move == enp_target and board[pos] % 8 == 1:
        if board[pos] // 8 == WHITE:
            board[enp_target-8] = 0
            black_pieces.remove(move-8)
            pieces.remove(move-8)
        else:
            board[enp_target+8] = 0
            white_pieces.remove(move+8)
            pieces.remove(move+8)

    # Castling
    if board[pos]%8 == 6 and abs(move-pos) == 2:
        if move == 6:
            performMove(7, 5)
        elif move == 2:
            performMove(0,3)
        elif move == 62:
            performMove(63, 61)
        elif move == 57:
            performMove(56, 58)

    if board[pos]//8 == WHITE:
        white_pieces.remove(pos)
        white_pieces.append(move)

        if board[move] != 0:
            black_pieces.remove(move)
    else:
        black_pieces.remove(pos)
        black_pieces.append(move)

        if board[move] != 0:
            white_pieces.remove(move)
    
    if board[pos] == 1 and move == pos+16: enp_target = pos+8
    elif board[pos] == 9 and move == pos-16: enp_target = pos-8

    board[move] = board[pos]
    board[pos] = 0

    if move not in pieces:
        pieces.append(move)

    pieces.remove(pos)

def newPerformMove(pos, move, board, pieces):
    global enp_target

    if move == enp_target and board[pos] % 8 == 1:
        if board[pos] // 8 == WHITE:
            board[enp_target-8] = 0
            black_pieces.remove(move-8)
            pieces.remove(move-8)
        else:
            board[enp_target+8] = 0
            white_pieces.remove(move+8)
            pieces.remove(move+8)

    # Castling
    if board[pos]%8 == 6 and abs(move-pos) == 2:
        if move == 6:
            performMove(7, 5, board)
        elif move == 2:
            performMove(0,3, board)
        elif move == 62:
            performMove(63, 61, board)
        elif move == 57:
            performMove(56, 58, board)

    if board[pos]//8 == WHITE:
        white_pieces.remove(pos)
        white_pieces.append(move)

        if board[move] != 0:
            black_pieces.remove(move)
    else:
        black_pieces.remove(pos)
        black_pieces.append(move)

        if board[move] != 0:
            white_pieces.remove(move)
    
    if board[pos] == 1 and move == pos+16: enp_target = pos+8
    elif board[pos] == 9 and move == pos-16: enp_target = pos-8

    board[move] = board[pos]
    board[pos] = 0

    if move not in pieces:
        pieces.append(move)

    pieces.remove(pos)

    return board, pieces

def getPotentialMoves():
    global potential_moves, board, white_check_pieces, black_check_pieces
    checks = [0, 0]
    
    for space in pieces:
        potential_moves[space] = move_dict[board[space]%8](board[space]//8, space)

    if inCheck(WHITE) == 1: checks[0] = 1
    elif inCheck(BLACK) == 1: checks[1] = 1

    for space in pieces:
        new_moves = []
        inc = checks[board[space] // 8]
        for move in potential_moves[space]:
            if checkLegality(space, move, inc) == 1: 
                new_moves.append(move)
        
        potential_moves[space] = [x for x in new_moves]

def getRandomMove(team):
    if team == WHITE:
        p = white_pieces
    else:
        p = black_pieces

    space = choice(p)
    while potential_moves[space] == []:
        space = choice(p)

    move = choice(potential_moves[space])

    return space, move

def inCheckmate(team):
    if inCheck(team) == 0: return 0

    if team == WHITE:
        p = white_pieces
    else:
        p = black_pieces

    for space in p:
        if potential_moves[space] != []: return 0
    
    return 1

def inStalemate(team):
    if inCheck(team) == 1: return 0

    if team == WHITE:
        p = white_pieces
    else:
        p = black_pieces

    for space in p:
        if potential_moves[space] != []: return 0

    return 1

def doPromotion(pos, team):
    global promotion
    if team == player == WHITE:
        promotion = 1
        x, y = posToXY(pos)
        rectangle = (x, y, 60, 240)
        screen.fill(PROMO_COLOR, rectangle)
        pieces = [2, 3, 4, 5]

        for piece in pieces:
            piece_image = pg.image.load(asset_directory + IMAGE_DIRECTORY[piece])
            screen.blit(piece_image, (x,y))
            y += 60

    elif team == player == BLACK:
        promotion = 1
        rectangle = (x, y+240, 60, 240)
        screen.fill(PROMO_COLOR, rectangle)
        pieces = [10, 11, 12, 13]

        for piece in pieces:
            piece_image = pg.image.load(asset_directory + IMAGE_DIRECTORY[piece])
            screen.blit(piece_image, (x,y))
            y -= 60

    elif team != player:
        global board

        if team == WHITE:
            board[pos] = 13
        elif team == BLACK:
            board[pos] = 5

def checkPromotion():
    for i in range(0, 8):
        if board[i] == 9: 
            doPromotion(i, BLACK)
            return i
    for i in range(56, 64):
        if board[i] == 1:
            doPromotion(i, WHITE)
            return i
    
    return -1

position = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -'
board = FENToBoard(position)

turn = WHITE
player = WHITE
piece_clicked = 0
clicked_space = -1

turnswap = 0




# Board Evaluation
PIECE_VALUES = {
    1: 100,
    2: 310,
    3: 330,
    4: 500,
    5: 900,
    6: 0
}

PAWN_PS = [0,  0,  0,  0,  0,  0,  0,  0, 
5, 10, 10,-20,-20, 10, 10,  5, 
5, -5,-10,  0,  0,-10, -5,  5, 
0,  0,  0, 20, 20,  0,  0,  0, 
5,  5, 10, 25, 25, 10,  5,  5, 
10, 10, 20, 30, 30, 20, 10, 10, 
50, 50, 50, 50, 50, 50, 50, 50, 
0,  0,  0,  0,  0,  0,  0,  0]

KNIGHT_PS = [-50,-40,-30,-30,-30,-30,-40,-50,
-40,-20,  0,  5,  5,  0,-20,-40,
-30,  5, 10, 15, 15, 10,  5,-30,
-30,  0, 15, 20, 20, 15,  0,-30,
-30,  5, 15, 20, 20, 15,  5,-30,
-30,  0, 10, 15, 15, 10,  0,-30,
-40,-20,  0,  0,  0,  0,-20,-40,
 -50,-40,-30,-30,-30,-30,-40,-50] 

BISHOP_PS = [-20,-10,-10,-10,-10,-10,-10,-20, 
-10,  5,  0,  0,  0,  0,  5,-10,
-10, 10, 10, 10, 10, 10, 10,-10,
-10,  0, 10, 10, 10, 10,  0,-10,
-10,  5,  5, 10, 10,  5,  5,-10,
-10,  0,  5, 10, 10,  5,  0,-10,
-10,  0,  0,  0,  0,  0,  0,-10,
-20,-10,-10,-10,-10,-10,-10,-20]

ROOK_PS = [  0,  0,  0,  5,  5,  0,  0,  0, 
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
  5, 10, 10, 10, 10, 10, 10,  5,
   0,  0,  0,  0,  0,  0,  0,  0]

QUEEN_PS = [-20,-10,-10, -5, -5,-10,-10,-20, 
-10,  0,  5,  0,  0,  0,  0,-10,
-10,  5,  5,  5,  5,  5,  0,-10,
  0,  0,  5,  5,  5,  5,  0, -5,
 -5,  0,  5,  5,  5,  5,  0, -5,
-10,  0,  5,  5,  5,  5,  0,-10,
-10,  0,  0,  0,  0,  0,  0,-10,
 -20,-10,-10, -5, -5,-10,-10,-20]

KING_PS = [20, 30, 10,  0,  0, 10, 30, 20,
20, 20,  0,  0,  0,  0, 20, 20,
-10,-20,-20,-20,-20,-20,-20,-10,
-20,-30,-30,-40,-40,-30,-30,-20,
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30]

PIECE_SQUARES = {
    1: PAWN_PS,
    2: KNIGHT_PS,
    3: BISHOP_PS,
    4: ROOK_PS,
    5: QUEEN_PS,
    6: KING_PS
}


def evaluateBoard(team, pieces, board):
    score = 0
    for space in pieces:
        piece = board[space]
        if piece < 8:
            score += PIECE_VALUES[piece]
            score += PIECE_SQUARES[piece][space]
        else:
            score -= PIECE_VALUES[piece - 8]
            score -= PIECE_SQUARES[piece - 8][64 - space]
    
    if team == WHITE: return score
    else: return  -score

def addMove(pos, move, team, pieces, board):
    piece = board[pos]
    score = 0

    if team == WHITE:
        if move in pieces: 
            score += PIECE_VALUES[board[move]-8]
            score += PIECE_SQUARES[board[move]-8][64-move]
        score -= PIECE_SQUARES[piece][pos]
        score += PIECE_SQUARES[piece[move]]
    else:
        if move in pieces: 
            score += PIECE_VALUES[board[move]]
            score += PIECE_SQUARES[board[move]][move]
        score -= PIECE_SQUARES[piece - 8][64 - pos]
        score += PIECE_SQUARES[piece - 8][64 - move]

    return score

def singleBestMove(pieces, team, board):
    best_score = -10000000
    best_move = [0, 0]
    for space in pieces:
        if board[space] // 8 == team:
            moves = potential_moves[space]

            for move in moves:
                score = addMove(space, move, team, pieces, board)

                if score > best_score:
                    best_score = score
                    best_move = [space, move]
    
    return best_move[0], best_move[1]

def treeSearch(team, alpha, depth):
    moves = []
    for space in pieces:
        for move in potential_moves[space]:
            moves.append([space, move])
    
    if depth == 1:
        team = not team
        base_score = evaluateBoard(team, pieces, board)
        best_score = -10000000
        best_move = [0, 0]

        for move in moves:
            score = base_score + addMove(move[0], move[1], team, pieces, board)
            best_score = max(score, best_score)

            if score > alpha:
                return 0, 10000000

    best_score = -10000000

    for move in moves:
        performMove(move[0], move[1])

        temp_move, temp_score = treeSearch(not team, -best_score, depth-1)
        performMove(move[1], move[0])
        temp_score = -temp_score

        if temp_score > best_score:
            best_score = temp_score
            best_move = move

        if temp_score > alpha:
            return 0, 1000000

    return best_move, best_score

def treeBestMove(team, alpha, depth):
    move, score = treeSearch(team, alpha, depth)
    return move[0], move[1]




# Stockfish
stockfish = sf.Stockfish(path= 'C:\Stuff\Games\Chess\stockfish_15_win_x64_popcnt\stockfish_15_x64_popcnt.exe', depth= 15)

def UCItoMove(ucimove):
    pos = ucimove[:2]
    move = ucimove[2:]

    pos = spaceToPos(pos)
    move = spaceToPos(move)

    return pos, move




# Game loop

getPotentialMoves()
while 1:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()
        if turn == player and turnswap == 0:
            if event.type == pg.MOUSEBUTTONUP:
                click_pos = pg.mouse.get_pos()
                space = XYToPos(click_pos[0], click_pos[1])

                if board[space] != 0 and board[space]//8 == turn: 
                    clicked_space = space
                elif clicked_space >= 0 and space in potential_moves[clicked_space]: 
                    turnswap = 1
                    performMove(clicked_space, space)

        if promotion:
            if event.type == pg.MOUSEBUTTONDOWN:
                click_pos = pg.mouse.get_pos()
                space = XYToPos(click_pos[0], click_pos[1])

                rank = getRank(space)
                if rank == 0: board[promosq] = 13
                elif rank == 1: board[promosq] = 12
                elif rank == 2: board[promosq] = 11
                elif rank == 3: board[promosq] = 10
                elif rank == 4: board[promosq] = 5
                elif rank == 5: board[promosq] = 4
                elif rank == 6: board[promosq] = 3
                elif rank == 7: board[promosq] = 2

                promotion = 0
                turnswap = 1
        



    if turn != player and turnswap == 0:
        space, move = treeBestMove(turn, 1000000, 1)
        performMove(space, move)
        turnswap = 1

    if turnswap == 1:
        turn = not turn
        white_threats = []
        black_threats = []
        white_check_pieces = []
        black_check_pieces = []
        getPotentialMoves()
        turnswap = 0
        clicked_space = -1
        updateCastles()

        if inCheckmate(turn): 
            print('Checkmate')
            turnswap = 2
        if inStalemate(turn): 
            print('Stalemate')
            turnswap = 2

    if getRank(enp_target) == 2 and turn == WHITE: enp_target = -1
    elif getRank(enp_target) == 5 and turn == BLACK: enp_target = -1

    displayBackground()
    if clicked_space >= 0:
        displayHighlight(clicked_space)
        displayMoves(potential_moves[clicked_space])

    displayPieces()

    promosq = checkPromotion()
    if promotion and turn != player:
        doPromotion(promosq, player)
        turnswap = 0
        turn = player

    pg.display.update()
    clock.tick(30)
