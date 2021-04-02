reverse_board_map = {
    'a': 1,
    'b': 2,
    'c': 3,
    'd': 4,
    'e': 5,
    'f': 6,
    'g': 7,
    'h': 8
}

global board 
board = [
    ["wr", "", "", "wk", "", "", "", "wr"],
    ["", "wp", "wp", "wp", "wp", "wp", "", "wp"],
    ["", "", "", "", "", "", "", ""],
    ["wp", "bp", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "wp", "bp"],
    ["", "", "", "", "", "", "", ""],
    ["bp", "", "bp", "bp", "bp", "bp", "bp", ""],
    ["br", "", "", "bk", "", "", "", "br"]
    ]
        
def is_stock_move_en_passant(stock_move):
    global board
    if board[int(stock_move[1]) - 1][8 - reverse_board_map[stock_move[0]]][1] == 'p':
        if stock_move[0] != stock_move[2]:
            if board[int(stock_move[3]) - 1][8 - reverse_board_map[stock_move[2]]] == "":
                return True
                
stock_move = "b5a6"


if stock_move == "e1g1":
    board[0][0] = ""
    board[0][1] = "wk"
    board[0][2] = "wr"
    board[0][3] = ""
elif stock_move == "e8g8":
    board[7][0] = ""
    board[7][1] = "bk"
    board[7][2] = "br"
    board[7][3] = ""
elif stock_move == "e1c1":
    board[0][3] = ""
    board[0][4] = "wr"
    board[0][5] = "wk"
    board[0][7] = ""
elif stock_move == "e8c8":
    board[7][3] = ""
    board[7][4] = "br"
    board[7][5] = "bk"
    board[7][7] = ""
elif len(stock_move) == 4:
    if is_stock_move_en_passant(stock_move):
        board[int(stock_move[1]) - 1][8 - reverse_board_map[stock_move[2]]] = ""
    board[int(stock_move[3]) - 1][8 - reverse_board_map[stock_move[2]]] = board[int(stock_move[1]) - 1][8 - reverse_board_map[stock_move[0]]]
    board[int(stock_move[1]) - 1][8 - reverse_board_map[stock_move[0]]] = ""
else:
    board[int(stock_move[3]) - 1][8 - reverse_board_map[stock_move[2]]] = board[int(stock_move[1]) - 1][8 - reverse_board_map[stock_move[0]]][0] + stock_move[len(stock_move) - 1]
    board[int(stock_move[1]) - 1][8 - reverse_board_map[stock_move[0]]] = ""

for element in board:
    print(element)