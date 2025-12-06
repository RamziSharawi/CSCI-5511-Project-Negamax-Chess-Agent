import chess
import chess.engine
import sys
import time
from players import AdvancedPlayer, RandomPlayer

# ================= CONFIGURATION =================
# PATH TO YOUR STOCKFISH EXECUTABLE (REQUIRED!)
STOCKFISH_PATH = "stockfish\stockfish-windows-x86-64-avx2.exe"

# Match settings
NUM_GAMES = 5          # Total games to play
STOCKFISH_ELO = 1600     # Stockfish strength

DEPTH_LIMIT = 4         # Both stop after depth 6
TIME_LIMIT  = 5.0     # Both have 10 seconds per move max

OPENING_BOOK = "opening_books\gm2600.bin" # Path to your .bin book (or None)
SYZYGY_PATH = None       # Path to Syzygy folder (or None)

# Time control for Stockfish (to keep it moving fast)
SF_MOVE_TIME = 0.1       # seconds per move for Stockfish
# =================================================

def play_game(game_id, agent_plays_white, engine):
    board = chess.Board()
    
    # Initialize your agent with the correct color for this game
    agent_color = chess.WHITE if agent_plays_white else chess.BLACK
    agent = AdvancedPlayer(
        mycolor=agent_color, 
        depth_limit=DEPTH_LIMIT,
        time_limit=TIME_LIMIT, 
        opening_book_path=OPENING_BOOK, 
        syzygy_path=SYZYGY_PATH
    )
    #opponent = RandomPlayer(mycolor=chess.WHITE if agent_color == chess.BLACK else chess.BLACK)

    print(f"Starting Game {game_id+1} (Agent is {'White' if agent_plays_white else 'Black'})...")
    
    while not board.is_game_over():
        if board.turn == agent_color:
            # --- Your Agent's Turn ---
            move = agent.make_move(board)
            board.push(move)
        else:
            # --- Stockfish's Turn ---
            result = engine.play(board, chess.engine.Limit(time=TIME_LIMIT, depth=DEPTH_LIMIT))
            board.push(result.move)
            # result = opponent.make_move(board)
            # board.push(result)

    # Game Over - Determine result
    result = board.result()

    moves_played = board.fullmove_number
    
    # Calculate who won relative to the Agent
    if result == "1/2-1/2":
        outcome = "Draw"
        score = 0.5
    elif (result == "1-0" and agent_plays_white) or (result == "0-1" and not agent_plays_white):
        outcome = "Agent Win"
        score = 1.0
    else:
        outcome = "Stockfish Win"
        score = 0.0

    print(f"Game {game_id+1} finished: {outcome} ({result}) in {moves_played} moves.")
    return score, moves_played

def main():
    print(f"--- STARTING MATCH: Agent vs Stockfish (Elo {STOCKFISH_ELO}) ---")
    print(f"Playing {NUM_GAMES} games...")

    try:
        # Initialize Stockfish once
        engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        engine.configure({"UCI_LimitStrength": True, "UCI_Elo": STOCKFISH_ELO})
    except FileNotFoundError:
        print(f"ERROR: Stockfish executable not found at: {STOCKFISH_PATH}")
        return

    agent_wins = 0
    sf_wins = 0
    draws = 0
    start_time = time.time()

    for i in range(NUM_GAMES):
        # Alternate colors every game
        agent_is_white = (i % 2 == 0)
        
        score, num_moves = play_game(i, agent_is_white, engine)
        
        if score == 1.0:
            agent_wins += 1
        elif score == 0.5:
            draws += 1
        else:
            sf_wins += 1

        # Optional: Print intermediate stats every 10 games
        if (i + 1) % 10 == 0:
            print(f"\n--- Stats after {i+1} games ---")
            print(f"Agent Wins: {agent_wins}")
            print(f"Stockfish Wins: {sf_wins}")
            print(f"Draws: {draws}")
            print("-----------------------------\n")

    engine.quit()
    
    total_time = time.time() - start_time
    print("\n================ MATCH RESULTS ================")
    print(f"Total Games: {NUM_GAMES}")
    print(f"Time Elapsed: {total_time/60:.2f} minutes")
    print("-----------------------------------------------")
    print(f"Agent Wins:     {agent_wins} ({agent_wins/NUM_GAMES*100:.1f}%)")
    print(f"Stockfish Wins: {sf_wins} ({sf_wins/NUM_GAMES*100:.1f}%)")
    print(f"Draws:          {draws} ({draws/NUM_GAMES*100:.1f}%)")
    print("===============================================")

if __name__ == "__main__":
    main()