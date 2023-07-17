from chess_functions import *

piece_values = {
    'k':20000,
    'q':900,
    'r':500,
    'n':320,
    'b':330,
    'p':100
}

wp_ps = [0,  0,  0,  0,  0,  0,  0,  0, 
5, 10, 10,-20,-20, 10, 10,  5, 
5, -5,-10,  0,  0,-10, -5,  5, 
0,  0,  0, 20, 20,  0,  0,  0, 
5,  5, 10, 25, 25, 10,  5,  5, 
10, 10, 20, 30, 30, 20, 10, 10, 
50, 50, 50, 50, 50, 50, 50, 50, 
0,  0,  0,  0,  0,  0,  0,  0]

wn_ps = [-50,-40,-30,-30,-30,-30,-40,-50,
-40,-20,  0,  5,  5,  0,-20,-40,
-30,  5, 10, 15, 15, 10,  5,-30,
-30,  0, 15, 20, 20, 15,  0,-30,
-30,  5, 15, 20, 20, 15,  5,-30,
-30,  0, 10, 15, 15, 10,  0,-30,
-40,-20,  0,  0,  0,  0,-20,-40,
 -50,-40,-30,-30,-30,-30,-40,-50] 

wb_ps = [-20,-10,-10,-10,-10,-10,-10,-20, 
-10,  5,  0,  0,  0,  0,  5,-10,
-10, 10, 10, 10, 10, 10, 10,-10,
-10,  0, 10, 10, 10, 10,  0,-10,
-10,  5,  5, 10, 10,  5,  5,-10,
-10,  0,  5, 10, 10,  5,  0,-10,
-10,  0,  0,  0,  0,  0,  0,-10,
-20,-10,-10,-10,-10,-10,-10,-20]

wr_ps = [  0,  0,  0,  5,  5,  0,  0,  0, 
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
  5, 10, 10, 10, 10, 10, 10,  5,
   0,  0,  0,  0,  0,  0,  0,  0]

wq_ps = [-20,-10,-10, -5, -5,-10,-10,-20, 
-10,  0,  5,  0,  0,  0,  0,-10,
-10,  5,  5,  5,  5,  5,  0,-10,
  0,  0,  5,  5,  5,  5,  0, -5,
 -5,  0,  5,  5,  5,  5,  0, -5,
-10,  0,  5,  5,  5,  5,  0,-10,
-10,  0,  0,  0,  0,  0,  0,-10,
 -20,-10,-10, -5, -5,-10,-10,-20]

wk_ps = [ 20, 30, 10,  0,  0, 10, 30, 20,
 20, 20,  0,  0,  0,  0, 20, 20,
-10,-20,-20,-20,-20,-20,-20,-10,
-20,-30,-30,-40,-40,-30,-30,-20,
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30]

wk_end_ps = [-50,-30,-30,-30,-30,-30,-30,-50,
-30,-30,  0,  0,  0,  0,-30,-30,
-30,-10, 20, 30, 30, 20,-10,-30,
-30,-10, 30, 40, 40, 30,-10,-30,
-30,-10, 30, 40, 40, 30,-10,-30,
-30,-10, 20, 30, 30, 20,-10,-30,
-30,-20,-10,  0,  0,-10,-20,-30,
-50,-40,-30,-20,-20,-30,-40,-50]

bp_ps = [x for x in wp_ps]
bn_ps = [x for x in wn_ps]
bb_ps = [x for x in wb_ps]
br_ps = [x for x in wr_ps]
bq_ps = [x for x in wq_ps]
bk_ps = [x for x in wk_ps]
bk_end_ps = [x for x in wk_end_ps]

bp_ps.reverse()
bn_ps.reverse()
bb_ps.reverse()
br_ps.reverse()
bq_ps.reverse()
bk_ps.reverse()
bk_end_ps.reverse()

ps_dict = {
    'p':[bp_ps, wp_ps],
    'n':[bn_ps, wn_ps],
    'b':[bb_ps, wb_ps],
    'r':[br_ps, wr_ps],
    'q':[bq_ps, wq_ps],
    'k':[bk_ps, wk_ps],
    'k_end':[bk_end_ps, wk_end_ps]
}

def evaluatePosition(team, board):
    score = 0
    pieces = getPieces(board)

    for space in pieces:
        piece = board[space]
        if piece.team == team:
            score += piece_values[piece.type]
            score += ps_dict[piece.type][piece.team][space]
        else:
            score -= piece_values[piece.type]
            score -= ps_dict[piece.type][piece.team][space]

    if team == 1 and inCheckmate(board) == 0:
        score = 100000
    elif team == 0 and inCheckmate(board) == 1:
        score = 100000

    return score    

def testMove(startpos, move, board): # Higher value = better move
    piece = board[startpos]

    current_score = ps_dict[piece.type][piece.team][startpos]
    new_score = ps_dict[piece.type][piece.team][move]

    pos_diff = new_score - current_score
    score_diff = 0

    if board[move] != ' ':
        captured_piece = board[move]
        captured_score = ps_dict[captured_piece.type][not piece.team][move] + piece_values[captured_piece.type]

        score_diff = pos_diff + captured_score
        
    
    else:
        score_diff = pos_diff
    
    return score_diff

def newScore(move, board, base_score):
    score = testMove(move[0], move[1], board)

    return base_score + score

def getScore(piece, space, team):
    return ps_dict[piece][team][space]