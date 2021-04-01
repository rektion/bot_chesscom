from stockfish import Stockfish
import os
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
import random

board_map = ['h', 'g', 'f', 'e', 'd', 'c', 'b', 'a']
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
bottom_left = [225, 570]
top_right = [729, 66]
board = []

def print_board():
    global board
    for ligne in board:
        for cell in ligne:
            print(" " if cell == "" else cell)


def check_dic_consistance(dic):
    sum = 0
    for key in dic:
        if len(dic[key]) == 3:
            return False
        sum += len(dic[key])
    return sum != 1


def check_dic_not_dupplicate_move(dic):
    for key in dic:
        if len(dic[key]) == 2:
            if dic[key][0] == dic[key][1]:
                return False
    return True


def update_new_board_from_str(string, new_board):
    last_two = string[len(string)-2:len(string)]
    if last_two.isdigit():
        x = last_two[1]
        y = last_two[0]
        piece = string[6:8]
    else:
        x = string[14]
        y = string[13]
        piece = last_two
    new_board[int(x)-1][abs(int(y)-1-7)] = piece
    return new_board


def from_diff_to_move(diff, promotion=None):
    key = list(diff.keys())[0]
    # hashmap = []
    # len = len(diff[key])
    # i = 0
    # while i < len:
    #     if diff[key][i] in hashmap:
    #         diff[key].pop(i)
    #         i -= 1
    #         len -= 1
    #     hashmap.append(diff[key][i])
    #     i += 1
    res = ""
    res += board_map[diff[key][0][1]]
    res += str(diff[key][0][0]+1)
    res += board_map[diff[key][1][1]]
    res += str(diff[key][1][0]+1)
    if promotion:
        res += promotion
    return res


def from_stock_move_to_cordonates(stock_move):
    res = []
    res.append([reverse_board_map[stock_move[0]], int(stock_move[1])])
    res.append([reverse_board_map[stock_move[2]], int(stock_move[3])])
    return res


def send_move_to_opponent(driver, stock_move, is_white):
    entire_board_elem = driver.find_element_by_xpath('//*[@id="board-layout-chessboard"]')
    entire_board_elem = entire_board_elem.find_element_by_tag_name('chess-board')
    coordonates = from_stock_move_to_cordonates(stock_move)
    source_piece_number = str(coordonates[0][0]) + str(coordonates[0][1])
    source = entire_board_elem.find_element_by_xpath(f"//*[contains(@class,'{source_piece_number}') and contains(@class,'piece')]")
    offset_x = (coordonates[1][0] - coordonates[0][0])*144 if is_white else (coordonates[0][0] - coordonates[1][0])*144
    offset_y = (coordonates[1][1] - coordonates[0][1])*144 if is_white else (coordonates[0][1] - coordonates[1][1])*144
    action = ActionChains(driver)
    action.drag_and_drop_by_offset(source, offset_x, -offset_y).perform() # 144*144


def actualiser_board(driver):
    entire_board_elem = driver.find_element_by_xpath('//*[@id="board-layout-chessboard"]')
    entire_board_elem = entire_board_elem.find_element_by_tag_name('chess-board')
    div_pieces = entire_board_elem.find_elements_by_xpath('.//*')
    new_board = [
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""]
    ]
    for piece in div_pieces:
        try:
            string = piece.get_attribute("class")
        except:
            return False
        if "piece" in string:
            new_board = update_new_board_from_str(string, new_board)
    global board
    board = new_board
    return True


def get_move_from_opponent(driver):
    global board
    diff = {}
    while diff == {} or not check_dic_consistance(diff) or not check_dic_not_dupplicate_move(diff):
        # On analyse le board en boucle jusqu'a ce qu'il y a une différence
        time.sleep(0.5) # verifier qu'il y a pas le pop up de win
        if len(driver.find_elements_by_xpath('//*[@id="board-layout-chessboard"]/div[3]/div')) == 1:
            return False
        entire_board_elem = driver.find_element_by_xpath('//*[@id="board-layout-chessboard"]')
        entire_board_elem = entire_board_elem.find_element_by_tag_name('chess-board')
        div_pieces = entire_board_elem.find_elements_by_xpath('.//*')
        new_board = [
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""]
        ]
        for piece in div_pieces:
            try:
                string = piece.get_attribute("class")
            except:
                return None
            if "piece" in string:
                new_board = update_new_board_from_str(string, new_board)
        diff = {}
        for i in range(8):
            for j in range(8):
                if board[i][j] != new_board[i][j]:
                    if board[i][j] != "" and new_board[i][j] != "":
                        piece = new_board[i][j]
                    else:
                        piece = board[i][j] if board[i][j] != "" else new_board[i][j]
                    if piece in diff:
                        if new_board[i][j] != "" and board[i][j] != piece:
                            diff[piece].append([i,j])
                        else:
                            diff[piece].insert(0,[i,j])
                    else:
                        diff[piece] = [[i,j]]
    board = new_board
    if "bk" in diff and "br" in diff:
        castle = abs(diff["br"][0][1] - diff["br"][1][1])
        if castle == 2:
            return "e8g8"
        else:
            return "e8c8"
    elif "wk" in diff and "wr" in diff:
        castle = abs(diff["wr"][0][1] - diff["wr"][1][1])
        if castle == 2:
            return "e1g1"
        else:
            return "e1c1"
    elif "wp" in diff and "wq" in diff:
        diff["wp"].append(diff["wq"][0])
        del diff["wq"]
        return from_diff_to_move(diff, promotion='q')
    elif "bp" in diff and "bq" in diff:
        diff["bp"].append(diff["bq"][0])
        del diff["bq"]
        return from_diff_to_move(diff, promotion='q')
    else:
        return from_diff_to_move(diff)

def create_driver(url, language):
    options = webdriver.ChromeOptions()
    options.add_argument("--user-agent=" + 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0')
    options.add_argument("--no-sandbox")
    # options.add_argument("--headless")
    options.add_argument("--no-first-run")
    driver = webdriver.Chrome(options=options, service_log_path=os.devnull)
    driver.set_page_load_timeout(30)
    driver.maximize_window()
    try:
        driver.get(url)
    except:
        if not bool(driver.find_elements_by_tag_name('head')):
            raise
    return driver

def login(driver):
    driver.find_element_by_xpath('//*[@id="username"]').send_keys("chassefaire.thibault3@gmail.com") # 2/3/4
    driver.find_element_by_xpath('//*[@id="password"]').send_keys("TEAM1777")
    driver.find_element_by_xpath('//*[@id="login"]').click()
    time.sleep(2)
    return driver

def lunch_game(driver):
    global board
    board = [
        ["wr", "wn", "wb", "wk", "wq", "wb", "wn", "wr"],
        ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
        ["br", "bn", "bb", "bk", "bq", "bb", "bn", "br"]
        ]
    try:
        driver.find_element_by_xpath('//*[@id="quick-link-new_game"]').click()
        time.sleep(2)
        new_game = driver.find_elements_by_xpath('//*[@id="board-layout-sidebar"]/div/div[2]/div/div[1]/div[1]/div/button')
    except:
        new_game = []
    if new_game == []:
        new_game = driver.find_elements_by_xpath('//*[@id="board-layout-sidebar"]/div/div[2]/div[1]/div[4]/div[1]/button[2]')
        if new_game == []:
            new_game = driver.find_elements_by_xpath('//*[@id="board-layout-sidebar"]/div/div[2]/div/div[3]/div[1]/button[2]')
    new_game[0].click()
    clock_str = driver.find_element_by_xpath('//*[@id="board-layout-player-top"]/div/div[2]/div/a[1]').text
    time.sleep(3)
    while clock_str == "Adversaire":
        time.sleep(1)
        clock_str = driver.find_element_by_xpath('//*[@id="board-layout-player-top"]/div/div[2]/div/a[1]').text
    print("L'adversaire est " + clock_str)
    clock_str = driver.find_element_by_xpath('//*[@id="board-layout-player-bottom"]/div/div[3]').get_attribute("class")
    print(clock_str)
    if "white" in clock_str:
        is_white = True
    elif "black" in clock_str:
        is_white = False
    else:
        print("ERROR WTFFFFFFFFFFFFFFFFFFFFFFFFF")
    return driver, is_white


stockfish = Stockfish("stockfish_x86-64-bmi2.exe", parameters={"Threads": 8, "Ponder": "true", "Skill Level": 7, "Hash": 512})
stockfish.set_depth(20)
driver = create_driver("https://www.chess.com/login_and_go", "en")
driver = login(driver)



driver, is_white = lunch_game(driver)
game_in_process = True
position = []
if not is_white:
    move = None
    while move == None:
        move = get_move_from_opponent(driver)
    position.append(move)
    stockfish.set_position(position) # entrée si noir 
while game_in_process:
    # print_board()
    # stock_move = stockfish.get_best_move_time(6000 + random.random()*2000)
    stock_move = stockfish.get_best_move()
    if len(position) > 14 and len(position) < 48:
        time.sleep(int(random.random()*7))
    print("les meilleur move est : " + stock_move)
    position.append(stock_move)
    send_move_to_opponent(driver, stock_move, is_white)
    while not actualiser_board(driver):
        pass
    stockfish.set_position(position)
    # print_board()
    move = None
    while move == None:
        move = get_move_from_opponent(driver)
    if move == False:
        break
    position.append(move)
    stockfish.set_position(position)