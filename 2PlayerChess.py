import pygame as pg
import math
from sys import exit

from regex import W

from evaluation import *

board = [' ' for i in range(64)]
asset_directory = 'Chess/assets/'

# Stuff
pg.init()

HEIGHT = 480
WIDTH = 480

screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Chess")

clock = pg.time.Clock()

# Piece object
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

file_list = 'abcdefgh'
# Graphics
background = pg.image.load("Chess/assets/board1.jpg").convert()
background = pg.transform.scale(background, (WIDTH, HEIGHT))

ring = pg.image.load("Chess/assets/ring.png")
ring = pg.transform.scale(ring, (60, 60))

PIECE_HIGHLIGHT = (252, 185, 234)
MOVES_HIGHLIGHT = (210, 210, 210) # The circle thingy
LEGAL_CAPTURE_HIGHLIGHT = (245, 158, 184)
LIGHT_SQUARE_COLOR = (233, 233, 233)
DARK_SQUARE_COLOR = (87, 144, 193)
PROMO_COLOR = (252, 185, 234)

wscore = 0
bscore = 0
game = True
ingame = True

promotion = False
able_promote = -1

# Starting Position


# Vars
game_state = 0 # Add later

state = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

xclick = -1
yclick = -1

moves = []

turn = 1
castle = {'K':1, 'Q':1, 'k': 1, 'q':1}
enpassant_target = '-'
halfmove_clock = 0
fullmove_num = 1

piece_clicked = False
clicked_space = -1

en_passant = -1
en_passant_turn = -1
kingPos = [60, 4] # black, white

# Frontend Stuff
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

def toXY(rank, file): # Turn a set of coordinates from 1-8 to 0-400
    return (file) * 60, 420 - (rank) * 60

def toRankFile(x,y): # Opposite of toXY
    return 7 - math.floor(y/60), math.floor(x/60)

def posToXY(pos): # The name
    rank, file = posToRankFile(pos)
    return toXY(rank, file)

def XYToPos(x, y): # The name
    rank, file = toRankFile(x, y)
    return(getPos(rank, file))

def posToRankFile(pos): # Gets the rank and file from a number 0-63
    rank = math.floor(pos/8)
    file = pos % 8

    return rank, file

def getPos(rank, file): # Returns a number 0-63 from rank,file
    return (rank * 8) + file

def displayPieces(): # Shows all pieces on board
    for i in range(64):
        square = board[i]
        if square == ' ':
                pass

        else:
            x, y = posToXY(i)

            piece_image = pg.image.load(square.image)
            screen.blit(piece_image, (x, y))

def showHighlight(pos): # Displays a highlight on a square
    x, y = posToXY(pos)
    screen.blit(ring, (x,y))
    
    rectangle = (x, y, 60, 60)
    screen.fill(PIECE_HIGHLIGHT, rect=rectangle)

# Board Representation
def getFEN(t, c, e, h, f): # Returns the FEN String from the board position
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

def FENToPos(fen): # Returns a board that reflects the FEN String
    parts = fen.split(' ')
    pieces_state = parts[0]

    pos = 0
    fenboard = [' ' for i in range(64)]

    board_state = pieces_state.split('/')
    board_state.reverse()
    
    for rank in board_state:
        for char in rank:
            if char.isdigit():
                pos += int(char)
            elif char != '/':
                fenboard[pos] = piece_dict[char]
                pos += 1

    return fenboard

# Piece Movements
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
                elif board[pos] != ' ' and board[i].team != board[pos].team:
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

def displayMoves(possible_moves): # Displays a list of positions
    for move in possible_moves:
        x, y = posToXY(move)
        
        if board[move] == ' ':
            pg.draw.circle(screen, MOVES_HIGHLIGHT, (x + 30, y + 30), 5)
        else:
            rectangle = (x, y, 60, 60)
            screen.fill(LEGAL_CAPTURE_HIGHLIGHT, rectangle)

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

def inCheck(board, kingPos): # Returns 0 if black in check, 1 if white, -1 if neither
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

    if piece != ' ' and inCheck(board, kingPos) == piece.team:
        for move in possible_moves:
            simboard = [x for x in board]
            simkingpos = kingPos

            simboard[move] = piece
            simboard[space] = ' '

            if piece.type == 'k':
                simkingpos[piece.team] = move

            if inCheck(simboard, simkingpos) != piece.team and inCheck(simboard, simkingpos) != 2:
                legal_moves.append(move)       
        return legal_moves

    for move in possible_moves:
        simboard = [x for x in board]
        simkingpos = kingPos

        simboard[move] = piece
        simboard[space] = ' '

        if piece != ' ' and piece.type == 'k':
            simkingpos[piece.team] = move

        if piece != ' ' and inCheck(simboard, simkingpos) != piece.team:
            legal_moves.append(move)

    return legal_moves

def inCheckmate(board, kingPos):
    if inCheck(board, kingPos) == 1:
        legal_moves = getLegalMoves('k', kingPos[1], board)
        if legal_moves == []:
            return 1
    elif inCheck(board, kingPos) == 0:
        legal_moves = getLegalMoves('k', kingPos[1], board)
        if legal_moves == []:
            return 0
    return -1

def checkEndGame(board, kingPos):
    global bscore, wscore, game, ingame
    if inCheckmate(board, kingPos) == 1:
        bscore += 1
        print('CHECKMATE! BLACK WINS!')
        ingame = False
    elif inCheckmate(board,kingPos) == 0:
        wscore += 1
        print('CHECKMATE! WHITE WINS')
        ingame = False
    
    pieces = [{
        'p':0,
        'b':0,
        'n':0,
        'r':0,
        'q':0,
        'k':0
    },{
        'p':0,
        'b':0,
        'n':0,
        'r':0,
        'q':0,
        'k':0
    }]

    total_pieces = [0, 0]
    for space in board:
        if space != ' ':
            pieces[space.team][space.type] += 1

            if space.team:
                total_pieces[1] += 1
            else:
                total_pieces[0] += 1
        
    if total_pieces[1] == 2:
        if total_pieces[0] == 2:
            if pieces[0]['b'] == 1 or pieces[0]['n'] == 1:
                if pieces[1]['b'] == 1 or pieces[1]['n'] == 1:
                    print('DRAW BY INSUFFICIENT MATERIAL')
                    ingame = False
        elif total_pieces[0] == 1:
             if pieces[1]['b'] == 1 or pieces[1]['n'] == 1:
                    print('DRAW BY INSUFFICIENT MATERIAL')
                    ingame = False
    elif total_pieces[1] == 1:
        if total_pieces[0] == 2:
            if pieces[0]['b'] == 1 or pieces[0]['n'] == 1:
                print('DRAW BY INSUFFICIENT MATERIAL')
                ingame = False
        elif total_pieces[0] == 1:
            print('DRAW BY INSUFFICIENT MATERIAL')
            ingame = False
    
    global turn
    stalemate = True
    for i in range(64):
        space = board[i]
        if space != ' ' and space.team == turn:
            if getLegalMoves(space.type, i, board) != []:
                stalemate = False
                break

    if stalemate:
        print('DRAW BY STALEMATE')
        ingame = False

def doPromotion(board, pos):
    x, y = posToXY(pos)
    if board[pos].team == 1:
        rectangle = (x, y, 60, 240)
        screen.fill(PROMO_COLOR, rectangle)
        pieces = [wq, wr, wb, wn]

        for piece in pieces:
            piece_image = pg.image.load(piece.image)
            screen.blit(piece_image, (x,y))
            y += 60
    elif board[pos].team == 0:
        rectangle = (x, y+240, 60, 240)
        screen.fill(PROMO_COLOR, rectangle)
        pieces = [bq, br, bb, bn]

        for piece in pieces:
            piece_image = pg.image.load(piece.image)
            screen.blit(piece_image, (x,y))
            y -= 60
    
    global promotion
    promotion = True

def checkPromotion(board):
    global able_promote
    for i in range(8):
        if board[i] != ' ' and board[i].type == 'p':
            able_promote = i
            doPromotion(board, i)
    
    for i in range(56, 64):
        if board[i] != ' ' and board[i].type == 'p':
            able_promote = i
            doPromotion(board, i)

# Pregame
board = FENToPos(state)
possible_moves = []

# Game Loop
while game:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()


        if event.type == pg.MOUSEBUTTONUP and not promotion:
            print(evaluatePosition(1, board))
            click_pos = pg.mouse.get_pos()
            space = XYToPos(click_pos[0], click_pos[1])

            if piece_clicked:
                if board[space] != ' ' and board[space].team == turn:
                    piece_clicked = True
                    clicked_space = space
                    possible_moves = getLegalMoves(board[clicked_space].type, clicked_space, board)
                if space in possible_moves:
                    # Castle
                    if board[clicked_space].type == 'k':
                        kingPos[turn] = space
                        if space == clicked_space + 2 or space == clicked_space - 2:
                            doCastle(space, board)
                        else:
                            removeCastle('k', clicked_space)

                    if en_passant != -1 and en_passant_turn == turn:
                        en_passant = -1
                        en_passant_turn = -1

                    if board[clicked_space].type == 'p':
                        halfmove_clock = 0
                        if (space == clicked_space + 16 and turn) or (space == clicked_space - 16 and not turn):
                            en_passant = space
                            en_passant_turn = turn
                            
                            rank, file = posToRankFile(en_passant)

                            if turn:
                                enpassant_target = file_list[file] + str(rank)
                            else:
                                enpassant_target = file_list[file] + str(rank + 2)

                    if board[clicked_space].type == 'r':
                        removeCastle('r', clicked_space)
                    
                    if board[clicked_space].type == 'p' and turn != en_passant_turn:
                        if turn and space == en_passant + 8:
                            board[en_passant] = ' '
                        elif not turn and space == en_passant - 8:
                            board[en_passant] = ' '
                    
                    if board[space] != ' ':
                        halfmove_clock = 0
            
                    board[space] = board[clicked_space]
                    board[clicked_space] = ' '
                    piece_clicked = False

                    if turn == 0:
                        fullmove_num += 1

                    turn = not turn
                    state = getFEN(turn, castle, enpassant_target, halfmove_clock, fullmove_num)

                    enpassant_target = '-'
                    halfmove_clock += 1

                else:
                    piece_clicked = False
                
            else:    
                if board[space] != ' ' and board[space].team == turn:
                    piece_clicked = True
                    clicked_space = space
                    
                    possible_moves = getLegalMoves(board[clicked_space].type, clicked_space, board)

        elif event.type == pg.MOUSEBUTTONUP and promotion:
            click_pos = pg.mouse.get_pos()
            space = XYToPos(click_pos[0], click_pos[1])

            if turn == 0:
                if space == able_promote:
                    board[able_promote] = wq
                elif space == able_promote - 8:
                    board[able_promote] = wr
                elif space == able_promote - 16:
                    board[able_promote] = wb
                elif space == able_promote - 24:
                    board[able_promote] = wn

            elif turn == 1:
                if space == able_promote:
                    board[able_promote] = bq
                elif space == able_promote + 8:
                    board[able_promote] = br
                elif space == able_promote + 16:
                    board[able_promote] = bb
                elif space == able_promote + 24:
                    board[able_promote] = bn
            
            promotion = False
            able_promote = -1

    displayBackground()

    if piece_clicked:
        showHighlight(space)
        displayMoves(possible_moves)
    
    displayPieces()
    checkPromotion(board)
    checkEndGame(board, kingPos)

    pg.display.update()
    clock.tick(30) # 30 FPS