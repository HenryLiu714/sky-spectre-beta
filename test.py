import stockfish as sf

# os.system('C:\Stuff\Games\Chess\stockfish_15_win_x64_popcnt\stockfish_15_x64_popcnt.exe')

stockfish = sf.Stockfish(path='C:\Stuff\Games\Chess\stockfish_15_win_x64_popcnt\stockfish_15_x64_popcnt.exe', depth=10)
stockfish.set_fen_position('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
print(stockfish.get_best_move(1000))
