import chess
import chess.engine
import sys
import time
from players import AdvancedPlayer, RandomPlayer
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
# ================= CONFIGURATION =================
# PATH TO YOUR STOCKFISH EXECUTABLE (REQUIRED!)
STOCKFISH_PATH = "stockfish\stockfish-windows-x86-64-avx2.exe"

# Match settings
NUM_GAMES = 100          # Total games to play
STOCKFISH_ELO = 1500     # Stockfish strength

DEPTH_LIMIT = 4         # Both stop after depth 6
TIME_LIMIT  = 5.0     # Both have 10 seconds per move max

OPENING_BOOK = "opening_books\gm2600.bin" # Path to your .bin book (or None)
SYZYGY_PATH = None       # Path to Syzygy folder (or None)

PLOT_FOLDER = "report_plots"
# =================================================

# - Function to predict the game phase at which the game finished.
def get_game_phase(board):
    """
    Determines the phase based on Non-Pawn Material (NPM).
    Weights: Queen=9, Rook=5, Knight=3, Bishop=3
    """
    # 1. Check for "Opening" based on low move count (blunder/trap)
    if board.fullmove_number <= 15:
        return "Opening"

    # 2. Calculate Non-Pawn Material for BOTH sides
    # We iterate over all piece types except Pawns and Kings
    piece_values = {
        chess.QUEEN: 9,
        chess.ROOK: 5,
        chess.BISHOP: 3,
        chess.KNIGHT: 3
    }
    
    total_material = 0
    for piece_type, value in piece_values.items():
        # Count white pieces of this type
        total_material += len(board.pieces(piece_type, chess.WHITE)) * value
        # Count black pieces of this type
        total_material += len(board.pieces(piece_type, chess.BLACK)) * value

    # 3. Define Phase based on Material Threshold
    # Max material is 62. 
    # A standard endgame threshold is often considered around 26 (e.g., Q+R vs Q+R is 28)
    if total_material <= 26:
        return "Endgame"
    else:
        return "Middlegame"


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
        winner = "Draw"
    elif (result == "1-0" and agent_plays_white) or (result == "0-1" and not agent_plays_white):
        winner = "Agent"
    else:
        winner = "Stockfish"

    phase = get_game_phase(board)
    
    game_data = {
        "Game_ID": game_id + 1,
        "Agent_Color": "White" if agent_plays_white else "Black",
        "Winner": winner,
        "Moves": moves_played,
        "Phase": phase
    }
    
    print(f"Game {game_id+1}: {winner} in {moves_played} moves ({phase})")
    return game_data

def generate_plots(df):
    if not os.path.exists(PLOT_FOLDER):
        os.makedirs(PLOT_FOLDER)
    sns.set_theme(style="whitegrid")
    
    # --- PLOT 1: Win Rates by Game Phase (Material Based) ---
    phase_order = ["Opening", "Middlegame", "Endgame"]
    df_grouped = df.groupby(['Phase', 'Winner']).size().reset_index(name='Counts')
    df_pivot = df_grouped.pivot(index='Phase', columns='Winner', values='Counts').fillna(0)
    df_pivot = df_pivot.reindex(phase_order)
    df_pct = df_pivot.div(df_pivot.sum(axis=1), axis=0) * 100
    
    ax = df_pct.plot(kind='bar', stacked=True, figsize=(10, 6), 
                     color={"Agent": "green", "Stockfish": "red", "Draw": "gray"})
    plt.title("Win/Loss Distribution by Game Phase (Material Based)",fontweight="bold")
    plt.ylabel("Percentage of Games (%)", fontweight="bold")
    plt.xlabel("Game Phase", fontweight="bold")
    plt.legend(title="Outcome", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_FOLDER, "plot_phase_performance.png"))
    print(f"Saved {PLOT_FOLDER}/plot_phase_performance.png")

    # --- PLOT 2: Elo Proxy (Performance by Color) ---
    plt.figure(figsize=(8, 6))
    # Using 'hue_order' ensures the colors stay consistent even if you have 0 draws
    sns.countplot(data=df, x="Agent_Color", hue="Winner", 
                  hue_order=["Agent", "Stockfish", "Draw"],
                  palette={"Agent": "green", "Stockfish": "red", "Draw": "gray"})
    plt.title("Elo Proxy: Agent Performance by Color", fontweight="bold")
    plt.ylabel("Number of Games", fontweight="bold")
    plt.xlabel("Agent Playing As", fontweight="bold")
    plt.savefig(os.path.join(PLOT_FOLDER, "plot_elo_proxy.png"))
    print(f"Saved {PLOT_FOLDER}/plot_elo_proxy.png")

    # --- PLOT 3: Game Length Distribution ---
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df, x="Moves", hue="Winner", multiple="stack", kde=True, 
                 hue_order=["Agent", "Stockfish", "Draw"],
                 palette={"Agent": "green", "Stockfish": "red", "Draw": "gray"})
    plt.title("Game Length Distribution", fontweight="bold")
    plt.xlabel("Full Moves", fontweight="bold")
    plt.savefig(os.path.join(PLOT_FOLDER, "plot_game_length_dist.png"))
    print(f"Saved {PLOT_FOLDER}/plot_game_length_dist.png")

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

    match_data = []
    agent_wins = 0
    sf_wins = 0
    draws = 0
    start_time = time.time()

    for i in range(NUM_GAMES):
        # Alternate colors every game
        agent_is_white = (i % 2 == 0)
        
        data = play_game(i, agent_is_white, engine)
        match_data.append(data)
        
        if data["Winner"] == "Agent":
            agent_wins += 1
        elif data["Winner"] == "Draw":
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

    df = pd.DataFrame(match_data)
    if not os.path.exists(PLOT_FOLDER): 
        os.makedirs(PLOT_FOLDER)
    df.to_csv(os.path.join(PLOT_FOLDER, "match_results.csv"), index=False)
    generate_plots(df)
if __name__ == "__main__":
    main()