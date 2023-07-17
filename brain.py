import math, random

from sympy import mod_inverse
from chess_functions import *
from evaluation import *

def treeSearch(team, alpha, depth, board):
    # if depth == 0:
    #     return 0, evaluatePosition(team, board)
    
    moves = getAllMoves(team, board)

    if depth == 1:
        base_score = evaluatePosition(team, board)
        best_score = -10000000
        best_move = [0, 0]

        for move in moves:
            score = newScore(move, board, base_score)
            best_score = max(score, best_score)

            if score > alpha:
                return 0, 10000000

        return 0, best_score

    
    best_score = -1000000
    best_move = [0, 0]

    for move in moves:
        simboard = [x for x in board]     
        performMove(move[0], move[1], simboard)
        
        temp_move, temp_score = treeSearch(not team, -best_score, depth-1, simboard)
        temp_score = -temp_score

        if temp_score > best_score:
            best_score = temp_score
            best_move = move

        if temp_score > alpha:
            return 0, 1000000

    return best_move, best_score
        