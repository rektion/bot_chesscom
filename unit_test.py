from stockfish import Stockfish
import datetime

stockfish = Stockfish("stockfish_x86-64-bmi2.exe", parameters={"Threads": 8, "Ponder": "True", "Skill Level": 6, "Hash": 512})
stockfish.set_depth(22)
stockfish.set_position(["e2e4", "e7e6"])
a = datetime.datetime.now()
print(stockfish.get_best_move())
b = datetime.datetime.now()
c = b - a
print(c.seconds)