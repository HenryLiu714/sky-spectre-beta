#include <iostream>
#include <bitset>
#include <vector>
#include <string>
#include <cstring>
#include <algorithm>
#include <map>
using namespace std;

typedef unsigned long long ull;

bool WHITE = 0;
bool BLACK = 1;

enum PieceType { // Piece type can be found by %8
    PAWN = 1,
    KNIGHT = 2,
    BISHOP = 3, 
    ROOK = 4,
    QUEEN = 5,
    KING = 6
};

enum ColorType { // <16 = W, >16 = B
    WH = 8,
    BL = 18
};

// %5 or %10 == 1,2,3 gives sliding pieces
// %10 gives piece type

int wPawn = 9;
int wKnight = 10;
int wBishop = 11;
int wRook = 12;
int wQueen3 = 13;
int wKing = 14;

int bPawn = 19;
int bKnight = 20;
int bBishop = 21;
int bRook = 22;
int bQueen = 23;
int bKing = 24;

int WCHECK = -1;
int BCHECK = -1;

int board[64] = {0};

bool WHITE_THREATS[64] = {0};
bool BLACK_THREATS[64] = {0};

int PINNED_SQUARES[64] = {0};
int inCheck = 2;

int len(string str)  {  // Length of a string
    int length = 0;  
    for (int i = 0; str[i] != '\0'; i++)  {  
        length++;  
          
    }  

    return length;     
}  

vector<string> split (string str, char seperator)  {  // Split string by seperator
    vector<string> strings;
    int currIndex = 0, i = 0;  
    int startIndex = 0, endIndex = 0;  
    while (i <= str.size())  {  
        if (str[i] == seperator || i == len(str))  {  
            endIndex = i;  
            string subStr = "";  
            subStr.append(str, startIndex, endIndex - startIndex);  
            strings.push_back(subStr);
            currIndex += 1;  
            startIndex = endIndex + 1;  
        }  
        i++;  
    }  

    return strings;
}  

int getRank(int pos) {
    return pos/8;
}

int getFile(int pos) {
    return pos % 8;
}

bool getTeam(int piece) {
    return piece > 16; 
}

int getType(int piece) {
    if (piece < 16) return piece % 8;
    else return piece % 18;
}

int isSliding(int piece) {
    int a = piece % 10; 

    if (a==1 || a==2 || a==3) {
        return true;
    }

    return false;
}

int getKingPos(bool team) {
    if (team == WHITE) {
        for (int i = 0; i < 64; i++) {
            if (board[i] == wKing) return i;
        }
    }

    else {
        for (int i = 0; i < 64; i++) {
            if (board[i] == bKing) return i;
        }
    }

    return 0;
}

bool noneBetween(int s1, int s2) { // Returns 1 if none between (pinned) or 0 if there is some between
    if (getFile(s1) == getFile(s2)) {
        int a = min(s1, s2);
        int b = max(s1, s2);

        for (int i = a+8; i < 64; i+=8) {
            if (i == b) return 1;
            else if (board[i] != 0) return 0;
        }
    }

    else if (getRank(s1) == getRank(s2)) {
        int a = min(s1, s2);
        int b = max(s1, s2);

        for (int i = a+1; i%8 != 0; i++) {
            if (i == b) return 1;
            else if (board[i] != 0) return 0;
        }
    }

    else if (s1 % 9 == s2 % 9) {
        int a = min(s1, s2);
        int b = max(s1, s2);

        for (int i = a+9; i%8 != 0 && i<64; i+=9) {
            if (i == b) return 1;
            else if (board[i] != 0) return 0;
        }
    }

    else if (s1 % 7 == s2 % 7) {
        int a = min(s1, s2);
        int b = max(s1, s2);

        for (int i = a+9; i%8 != 7 && i<64; i+=7) {
            if (i == b) return 1;
            else if (board[i] != 0) return 0;
        }
    }

    return 0;
}

vector<int> pawnMoves(bool team, int pos) {

    vector<int> moves;
    int rank = getRank(pos);
    int file = getFile(pos);

    if (team == WHITE) {
        if (board[pos+8] == 0) moves.push_back(pos+8);

        if (rank == 1 && board[pos+16] == 0) moves.push_back(pos+16);

        if (file == 0) {
            if (board[pos+9] == 0) WHITE_THREATS[pos+9] = 1;

            else if (getTeam(board[pos+9]) == BLACK) {
                moves.push_back(pos+9);
                WHITE_THREATS[pos+9] = 1;
            }
        }

        else if (file == 7) {
            if (board[pos+7] == 0) WHITE_THREATS[pos+7] = 1;

            else if (getTeam(board[pos+7]) == BLACK) {
                moves.push_back(pos+7);
                WHITE_THREATS[pos+7] = 1;
            }
        }

        else {
            if (board[pos+9] == 0) WHITE_THREATS[pos+9] = 1;

            else if (getTeam(board[pos+9]) == BLACK) {
                moves.push_back(pos+9);
                WHITE_THREATS[pos+9] = 1;
            }

            if (board[pos+7] == 0) WHITE_THREATS[pos+7] = 1;

            else if (getTeam(board[pos+7]) == BLACK) {
                moves.push_back(pos+7);
                WHITE_THREATS[pos+7] = 1;
            }
        }
    }

    else {
        if (board[pos-8] == 0) moves.push_back(pos-8);

        if (rank == 6 && board[pos-16] == 0) moves.push_back(pos-16);

        if (file == 7) {
            if (board[pos-9] == 0) BLACK_THREATS[pos-9] = 1;

            else if (getTeam(board[pos-9]) == BLACK) {
                moves.push_back(pos-9);
                BLACK_THREATS[pos-9] = 1;
            }
        }

        else if (file == 0) {
            if (board[pos-7] == 0) BLACK_THREATS[pos-7] = 1;

            else if (getTeam(board[pos-7]) == BLACK) {
                moves.push_back(pos-7);
                BLACK_THREATS[pos-7] = 1;
            }
        }

        else {
            if (board[pos-9] == 0) BLACK_THREATS[pos-9] = 1;

            else if (getTeam(board[pos-9]) == BLACK) {
                moves.push_back(pos-9);
                BLACK_THREATS[pos-9] = 1;
            }

            if (board[pos-7] == 0) BLACK_THREATS[pos-7] = 1;

            else if (getTeam(board[pos-7]) == BLACK) {
                moves.push_back(pos-7);
                BLACK_THREATS[pos-7] = 1;
            }
        }
    }

    return moves;
}

bool knightValid(int pos, int move, bool team) {
    if (move < 0 || move > 63) {
        return false;
    }

    int diff = getFile(pos) - getFile(move);

    if (diff == 2 || diff == 1 || diff == -1 || diff == -2) {
        if (getTeam(board[move]) != team) {
            return true;
        }
    }

    return false;
}

vector<int> knightMoves(bool team, int pos) {
    vector<int> moves;
    
    int possible_moves[] = {pos + 10, pos - 10, pos + 6, pos - 6, pos + 15, pos - 15, pos + 17, pos - 17};

    for (int i = 0; i < 8; i++) {
        if (knightValid(pos, possible_moves[i], team)) moves.push_back(possible_moves[i]);
    }

    return moves;
}

vector<int> bishopMoves(bool team, int pos) {
    vector<int> moves;

    int kingPos = getKingPos(!team);

    for (int i = pos+9; i<64 && i%8 != 0; i+=9) {
        if (board[i] != 0) {
            if (team == WHITE && getTeam(board[i]) == BLACK) {
                moves.push_back(i);
                WHITE_THREATS[i] = 1;
                
                if (noneBetween(i, kingPos)) PINNED_SQUARES[i] = pos;
            }

            else if (team == BLACK && getTeam(board[i]) == WHITE) {
                moves.push_back(i);
                BLACK_THREATS[i] = 1;

                if (noneBetween(i, kingPos)) PINNED_SQUARES[i] = pos;
            }
        }

        else {
            moves.push_back(i);
        }
    }

    for (int i = pos+7; i<64 && i%8 != 7; i+=7) {
        if (board[i] != 0) {
            if (team == WHITE && getTeam(board[i]) == BLACK) {
                moves.push_back(i);
                WHITE_THREATS[i] = 1;
                
                if (noneBetween(i, kingPos)) PINNED_SQUARES[i] = pos;
            }

            else if (team == BLACK && getTeam(board[i]) == WHITE) {
                moves.push_back(i);
                BLACK_THREATS[i] = 1;

                if (noneBetween(i, kingPos)) PINNED_SQUARES[i] = pos;
            }
        }

        else {
            moves.push_back(i);
        }
    }

    for (int i = pos-9; i>=0 && i%8 != 7; i-=9) {
        if (board[i] != 0) {
            if (team == WHITE && getTeam(board[i]) == BLACK) {
                moves.push_back(i);
                WHITE_THREATS[i] = 1;
                
                if (noneBetween(i, kingPos)) PINNED_SQUARES[i] = pos;
            }

            else if (team == BLACK && getTeam(board[i]) == WHITE) {
                moves.push_back(i);
                BLACK_THREATS[i] = 1;

                if (noneBetween(i, kingPos)) PINNED_SQUARES[i] = pos;
            }
        }

        else {
            moves.push_back(i);
        }
    }

    for (int i = pos-7; i>=0 && i%8 != 0; i-=7) {
        if (board[i] != 0) {
            if (team == WHITE && getTeam(board[i]) == BLACK) {
                moves.push_back(i);
                WHITE_THREATS[i] = 1;
                
                if (noneBetween(i, kingPos)) PINNED_SQUARES[i] = pos;
            }

            else if (team == BLACK && getTeam(board[i]) == WHITE) {
                moves.push_back(i);
                BLACK_THREATS[i] = 1;

                if (noneBetween(i, kingPos)) PINNED_SQUARES[i] = pos;
            }
        }

        else {
            moves.push_back(i);
        }
    }

    return moves;
}

vector<int> rookMoves(bool team, int pos) {
    vector<int> moves;

    int kingPos = getKingPos(!team);

    for (int i = pos+1; i%8 != 0; i+=1) {
        if (board[i] != 0) {
            if (team == WHITE && getTeam(board[i]) == BLACK) {
                moves.push_back(i);
                WHITE_THREATS[i] = 1;
                
                if (noneBetween(i, kingPos)) PINNED_SQUARES[i] = pos;
            }

            else if (team == BLACK && getTeam(board[i]) == WHITE) {
                moves.push_back(i);
                BLACK_THREATS[i] = 1;

                if (noneBetween(i, kingPos)) PINNED_SQUARES[i] = pos;
            }
        }

        else {
            moves.push_back(i);
        }
    }

    for (int i = pos+8; i<64; i+=8) {
        if (board[i] != 0) {
            if (team == WHITE && getTeam(board[i]) == BLACK) {
                moves.push_back(i);
                WHITE_THREATS[i] = 1;
                
                if (noneBetween(i, kingPos)) PINNED_SQUARES[i] = pos;
            }

            else if (team == BLACK && getTeam(board[i]) == WHITE) {
                moves.push_back(i);
                BLACK_THREATS[i] = 1;

                if (noneBetween(i, kingPos)) PINNED_SQUARES[i] = pos;
            }
        }

        else {
            moves.push_back(i);
        }
    }

    for (int i = pos-1; i%8 != 7; i-=1) {
        if (board[i] != 0) {
            if (team == WHITE && getTeam(board[i]) == BLACK) {
                moves.push_back(i);
                WHITE_THREATS[i] = 1;
                
                if (noneBetween(i, kingPos)) PINNED_SQUARES[i] = pos;
            }

            else if (team == BLACK && getTeam(board[i]) == WHITE) {
                moves.push_back(i);
                BLACK_THREATS[i] = 1;

                if (noneBetween(i, kingPos)) PINNED_SQUARES[i] = pos;
            }
        }

        else {
            moves.push_back(i);
        }
    }

    for (int i = pos-8; i>=0; i-=8) {
        if (board[i] != 0) {
            if (team == WHITE && getTeam(board[i]) == BLACK) {
                moves.push_back(i);
                WHITE_THREATS[i] = 1;
                
                if (noneBetween(i, kingPos)) PINNED_SQUARES[i] = pos;
            }

            else if (team == BLACK && getTeam(board[i]) == WHITE) {
                moves.push_back(i);
                BLACK_THREATS[i] = 1;

                if (noneBetween(i, kingPos)) PINNED_SQUARES[i] = pos;
            }
        }

        else {
            moves.push_back(i);
        }
    }

    return moves;
}

vector<int> queenMoves(bool team, int pos) {
    vector<int> bmoves = bishopMoves(team, pos);
    vector<int> rmoves = rookMoves(team, pos);

    for (int i = 0; i < rmoves.size(); i++) {
        bmoves.push_back(rmoves[i]);
    }

    return bmoves;
}
