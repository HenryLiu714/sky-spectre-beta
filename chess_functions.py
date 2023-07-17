import random, math
from numba import jit

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

def getKingPos(board):
    kp = [0, 0]
    for i in range(64):
        if board[i] != ' ' and board[i].type == 'k':
            kp[board[i].team] = i
    
    return kp

def toXY(rank, file): # Turn a set of coordinates from 1-8 to 0-400
    return (file) * 60, 420 - (rank) * 60

def toRankFile(x,y): # Opposite of toXY
    return 7 - math.floor(y/60), math.floor(x/60)

def posToXY(pos): # The name
    rank, file = posToRankFile(pos)
    return toXY(rank, file)

def getFEN(t, c, e, h, f, board): # Returns the FEN String from the board position
    rString = ''
    count = 0

    for rank in range(7, -1, -1):
        for file in range(8):
            if board[getPos(rank, file)] == ' ':
                count += 1
            else:
                if count > 0:
                    rString += str(count)
                    count = 0
                
                piece = board[getPos(rank,file)]
                if piece.team:
                    rString += piece.type.upper()
                else:
                    rString += piece.type
        if count > 0:
            rString += str(count)
            count = 0
        
        if rank != 0:
            rString += '/'

    rString += ' '
    
    if t:
        rString += 'w '
    else:
        rString += 'b '
    
    castles = [k for k, v in c.items() if v]
    
    for char in castles:
        rString += char

    rString += ' '
    rString += e + ' '

    rString += str(h) + ' ' + str(f)

    return rString

def XYToPos(x, y): # The name
    rank, file = toRankFile(x, y)
    return(getPos(rank, file))

def posToRankFile(pos): # Gets the rank and file from a number 0-63
    rank = math.floor(pos/8)
    file = pos % 8

    return rank, file

def getPos(rank, file): # Returns a number 0-63 from rank,file
    return (rank * 8) + file

 
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

 
def BMoves(pos, board): # For bishop
    i = pos
    possible_moves = []
    
    rank, file = posToRankFile(pos)
    team = board[pos].team

    counter = file + 1
    i = pos + 9
    while i < 64 and counter < 8:
        if board[i] == ' ':
            possible_moves.append(i)
        elif board[i].team == team:
            break
        else:
            possible_moves.append(i)
            break
        
        i += 9
        counter += 1

    i = pos + 7
    counter = file - 1
    while i < 64 and counter >= 0:
        if board[i] == ' ':
            possible_moves.append(i)
        elif board[i].team == team:
            break
        else:
            possible_moves.append(i)
            break
            
        i += 7
        counter -= 1

    i = pos - 9
    counter = file - 1 
    while i >= 0 and counter >= 0:
        if board[i] == ' ':
            possible_moves.append(i)
        elif board[i].team == team:
            break
        else:
            possible_moves.append(i)
            break
        
        i -= 9
        counter -= 1

    i = pos - 7
    counter = file + 1
    while i >= 0 and counter < 8:
        if board[i] == ' ':
            possible_moves.append(i)
        elif board[i].team == team:
            break
        else:
            possible_moves.append(i)
            break
        
        i -= 7
        counter += 1

    return possible_moves

   
def RMoves(pos, board): # For rook
    i = pos
    possible_moves = []

    rank, file = posToRankFile(pos)
    team = board[pos].team
    
    counter = file + 1
    i = pos + 1
    while counter < 8:
        if board[i] == ' ':
            possible_moves.append(i)
        elif board[i].team == team:
            break
        else:
            possible_moves.append(i)
            break
        counter += 1
        i += 1
    
    counter = file - 1
    i = pos - 1
    while counter >= 0:
        if board[i] == ' ':
            possible_moves.append(i)
        elif board[i].team == team:
            break
        else:
            possible_moves.append(i)
            break
        
        counter -= 1
        i -= 1

    counter = rank + 1
    i = pos + 8
    while counter < 8:
        if board[i] == ' ':
            possible_moves.append(i)
        elif board[i].team == team:
            break
        else:
            possible_moves.append(i)
            break
        counter += 1
        i += 8

    counter = rank - 1
    i = pos - 8
    while counter >= 0:
        if board[i] == ' ':
            possible_moves.append(i)
        elif board[i].team == team:
            break
        else:
            possible_moves.append(i)
            break
        counter -= 1
        i -= 8

    return possible_moves

 
def QMoves(pos, board): # For queen
    rmoves = RMoves(pos, board)
    bmoves = BMoves(pos, board)

    possible_moves = rmoves + bmoves
    return possible_moves

 
def NMoves(pos, board): # For knight
    possible_moves = [pos + 10, pos - 10, pos + 6, pos - 6, pos + 15, pos - 15, pos + 17, pos - 17]
    possible_moves2 = []
    rank, file = posToRankFile(pos)

    for i in possible_moves:
        if abs(posToRankFile(i)[1] - file) == 1 or abs(posToRankFile(i)[1] - file) == 2:
            if i < 64 and i >= 0:
                if board[i] == ' ':
                    possible_moves2.append(i)
                elif board[i].team != board[pos].team:
                    possible_moves2.append(i)
    
    return possible_moves2

 
def KMoves(pos, board):
    possible_moves = [pos+1, pos-1, pos-7, pos+7, pos-9, pos+9, pos+8, pos-8]
    rank, file = posToRankFile(pos)

    possible_moves2 = []
    
    for i in possible_moves:
        if abs(posToRankFile(i)[1] - file) == 1 or abs(posToRankFile(i)[1] - file) == 0:
            if i < 64 and i >= 0:
                if board[i] == ' ':
                    possible_moves2.append(i)
                elif board[i].team != board[pos].team:
                    possible_moves2.append(i)

    # Castles
    if turn:
        if castle['K']:
            if board[5] == ' ' and board[6] == ' ':
                possible_moves2.append(6)
        if castle['Q']:
            if board[1] == ' ' and board[2] == ' ' and board[3] == ' ':
                possible_moves2.append(2)
    else:
        if castle['k']:
            if board[61] == ' ' and board[62] == ' ':
                possible_moves2.append(62)
        if castle['q']:
            if board[57] == ' ' and board[58] == ' ' and board[59] == ' ':
                possible_moves2.append(58)
    
    return possible_moves2

moves_dict = {
    'p':PMoves,
    'b':BMoves,
    'r':RMoves,
    'q':QMoves,
    'n':NMoves,
    'k':KMoves
}

def doCastle(type, board):
    if type == 6:
        board[5] = wr
        board[7] = ' '
        castle['K'] = False

    elif type == 2:
        board[3] = wr
        board[0] = ' '
        castle['Q'] = False

    elif type == 62:
        board[61] = br
        board[63] = ' '
        castle['k'] = False

    elif type == 58:
        board[59] = br
        board[56] = ' '
        castle['q'] = False

def removeCastle(type, clicked_space): # Turn castle vars to false
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

 
def getPossibleMoves(type, space, board):
    if type != 'p':
        possible_moves = moves_dict[type](space, board)
    elif type == 'p':
        possible_moves, capture_moves = moves_dict[type](space, board)
    possible_moves2 = []
    
    for move in possible_moves:
        if board[move] == ' ':
            possible_moves2.append(move)
        elif board[move].team != board[space].team:
            if type != 'p':
                possible_moves2.append(move)
            elif type == 'p':
                if move in capture_moves:
                    possible_moves2.append(move)

    return possible_moves2

 
def getCaptureMoves(type, space, board):
    if type != 'p':
        capture_moves = moves_dict[type](space, board)
    elif type == 'p':
        possible_moves, capture_moves = moves_dict[type](space, board)
    possible_moves2 = []
    
    for move in capture_moves:
        if board[move] == ' ':
            possible_moves2.append(move)
        elif board[move].team != board[space].team:
            possible_moves2.append(move)

    return possible_moves2

 
def inCheck(board): # Returns 0 if black in check, 1 if white, -1 if neither
    kingPos = getKingPos(board)
    possible_moves = []
    whiteInCheck = False
    blackInCheck = False
    for i in range(64):
        if board[i] != ' ':
            piece = board[i]
            possible_moves = getCaptureMoves(piece.type, i, board)

            if kingPos[0] in possible_moves and board[i].team:
                blackInCheck = True
            elif kingPos[1] in possible_moves and not board[i].team:
                whiteInCheck = True
    
    if whiteInCheck and blackInCheck:
        return 2
    elif whiteInCheck:
        return 1
    elif blackInCheck:
        return 0
    return -1

 
def getLegalMoves(type, space, board):
    possible_moves = getPossibleMoves(type, space, board)
    piece = board[space]

    legal_moves = []

    if inCheck(board) == piece.team:
        for move in possible_moves:
            simboard = [x for x in board]

            simboard[move] = piece
            simboard[space] = ' '

            if inCheck(simboard) != piece.team and inCheck(simboard) != 2:
                legal_moves.append(move)
        return legal_moves

    for move in possible_moves:
        simboard = [x for x in board]

        simboard[move] = piece
        simboard[space] = ' '

        if inCheck(simboard) != piece.team:
            legal_moves.append(move)

    return legal_moves

 
def inCheckmate(board):
    kingPos = getKingPos(board)
    if inCheck(board) == 1:
        if getLegalMoves('k', kingPos[1], board) != []:
            return -1

        all_moves = []

        for i in range(64):
            if board[i] != ' ' and board[i].team == 1:
                legal_moves = getLegalMoves(board[i].type, i, board)
                for x in legal_moves:
                    all_moves.append(x)
        if all_moves == []:
            return 1
    elif inCheck(board) == 0:
        if getLegalMoves('k', kingPos[0], board) != []:
            return -1

        all_moves = []

        for i in range(64):
            if board[i] != ' ' and board[i].team == 0:
                legal_moves = getLegalMoves(board[i].type, i, board)
                for x in legal_moves:
                    all_moves.append(x)
        if all_moves == []:
            return 0
    return -1

 
def performMove(startPos, move, board):
    board[move] = board[startPos]
    board[startPos] = ' '

    return board

def getPieces(board):
    pieces = []
    for i in range(64):
        if board[i] != ' ':
            pieces.append(i)
    
    return pieces

 
def getAllMoves(team, board):
    pieces = getPieces(board)
    moves = []

    for space in pieces:
        if board[space].team == team:
            legal_moves = getLegalMoves(board[space].type, space, board)

            for move in legal_moves:
                if board[move] in pieces:
                    moves.insert(0, [space,move])
                else:
                    moves.append([space, move])
    
    return moves