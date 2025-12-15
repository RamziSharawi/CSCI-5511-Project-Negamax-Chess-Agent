import chess
import chess.engine
import sys
import argparse
import time
from players import RAMZPlayer, RandomPlayer, StockfishPlayer
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
# ================= CONFIGURATION =================
# PATH TO YOUR STOCKFISH EXECUTABLE (REQUIRED!)
DEFAULT_STOCKFISH = r"stockfish\stockfish-windows-x86-64-avx2.exe"
DEFAULT_BOOK = r"opening_books\gm2600.bin"
PLOT_FOLDER = "report_plots"

# Match settings
DEFAULT_NUM_GAMES = 100          # Total games to play
DEFAULT_STOCKFISH_ELO = 1500     # Stockfish strength

DEFAULT_DEPTH_LIMIT = 4         # Both stop after depth 6print(f"Game {game_id+1}: {winner_name.title()} wins in {moves} moves ({phase})")
DEFAULT_TIME_LIMIT  = 5.0     # Both have 10 seconds per move max

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

def create_player(agent_type, color, args):
    """
    Factory function to instantiate the correct player based on string name.
    """
    agent_type = agent_type.lower()
    
    if agent_type == 'ramz':
        return RAMZPlayer(
            mycolor=color,
            depth_limit=args.depth,
            time_limit=args.time,
            opening_book_path=DEFAULT_BOOK,
            syzygy_path=None
        )
    elif agent_type == 'stockfish':
        return StockfishPlayer(
            color=color,
            path=DEFAULT_STOCKFISH,
            depth_limit=args.depth,
            time_limit=args.time,
            elo=args.elo
        )
    elif agent_type == 'random':
        return RandomPlayer(mycolor=color)
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")


def play_game(game_id, p1_type, p2_type, p1_plays_white, args):
    board = chess.Board()
    
    # Determine colors
    p1_color = chess.WHITE if p1_plays_white else chess.BLACK
    p2_color = chess.BLACK if p1_plays_white else chess.WHITE

    # Instantiate Players
    # We instantiate fresh every game to ensure clean state (empty TT, clean process)
    player1 = create_player(p1_type, p1_color, args)
    player2 = create_player(p2_type, p2_color, args)

    white_player = player1 if p1_plays_white else player2
    black_player = player2 if p1_plays_white else player1

    print(f"Game {game_id+1}: {p1_type.title()} ({'White' if p1_plays_white else 'Black'}) vs {p2_type.title()}")

    while not board.is_game_over():
        if board.turn == chess.WHITE:
            move = white_player.make_move(board)
        else:
            move = black_player.make_move(board)
        
        board.push(move)

    # Cleanup (Important for Stockfish processes)
    if hasattr(player1, 'close'): player1.close()
    if hasattr(player2, 'close'): player2.close()

    # Determine Winner
    result = board.result()
    if result == "1/2-1/2":
        winner_name = "Draw"
    elif result == "1-0":
        winner_name = p1_type if p1_plays_white else p2_type
    else: # 0-1
        winner_name = p2_type if p1_plays_white else p1_type

    phase = get_game_phase(board)
    moves = board.fullmove_number

    print(f"Game {game_id+1}: {winner_name.title()} wins in {moves} moves ({phase})")
    
    # Return data relative to Player 1
    return {
        "Game_ID": game_id + 1,
        "P1_Color": "White" if p1_plays_white else "Black",
        "Winner": winner_name.title(), # e.g. "RAM-Z", "Stockfish", "Draw"
        "Moves": board.fullmove_number,
        "Phase": phase
    }

def generate_plots(df, p1_name, p2_name):
    if not os.path.exists(PLOT_FOLDER):
        os.makedirs(PLOT_FOLDER)
    sns.set_theme(style="whitegrid")
    
    # standardized colors
    colors = {p1_name.title(): "green", p2_name.title(): "red", "Draw": "gray"}

    # --- PLOT 1: Win Rates by Game Phase ---
    phase_order = ["Opening", "Middlegame", "Endgame"]
    df_grouped = df.groupby(['Phase', 'Winner']).size().reset_index(name='Counts')
    df_pivot = df_grouped.pivot(index='Phase', columns='Winner', values='Counts').fillna(0)
    # Ensure all columns exist
    for col in [p1_name.title(), p2_name.title(), "Draw"]:
        if col not in df_pivot.columns: df_pivot[col] = 0
            
    df_pivot = df_pivot.reindex(phase_order)
    df_pct = df_pivot.div(df_pivot.sum(axis=1), axis=0) * 100
    
    ax = df_pct.plot(kind='bar', stacked=True, figsize=(10, 6), color=colors)
    plt.title("Win/Loss Distribution by Game Phase", fontweight="bold")
    plt.ylabel("Percentage of Games (%)", fontweight="bold")
    plt.savefig(os.path.join(PLOT_FOLDER, "plot_phase.png"))
    print(f"Saved {PLOT_FOLDER}/plot_phase.png")

    # --- PLOT 2: Performance by Color ---
    plt.figure(figsize=(8, 6))
    sns.countplot(data=df, x="P1_Color", hue="Winner", hue_order=[p1_name.title(), p2_name.title(), "Draw"], palette=colors)
    plt.title(f"{p1_name.title()} Performance by Color", fontweight="bold")
    plt.xlabel(f"{p1_name.title()} Playing As", fontweight="bold")
    plt.savefig(os.path.join(PLOT_FOLDER, "plot_color_perf.png"))
    print(f"Saved {PLOT_FOLDER}/plot_color_perf.png")

    # --- PLOT 3: Game Length ---
    plt.figure(figsize=(10, 6))
    try:
        sns.histplot(data=df, x="Moves", hue="Winner", multiple="stack", kde=True, 
                     hue_order=[p1_name.title(), p2_name.title(), "Draw"], palette=colors)
        plt.title("Game Length Distribution", fontweight="bold")
        plt.savefig(os.path.join(PLOT_FOLDER, "plot_length.png"))
        print(f"Saved {PLOT_FOLDER}/plot_length.png")
    except Exception as e:
        print(f"Could not generate histogram (maybe not enough data?): {e}")

def main():
    parser = argparse.ArgumentParser(description="Chess Agent Match Runner")
    
    # Agent Settings
    parser.add_argument('--agent1', type=str, default='ramz', choices=['ramz', 'stockfish', 'random'], help="First agent (Player 1)")
    parser.add_argument('--agent2', type=str, default='stockfish', choices=['ramz', 'stockfish', 'random'], help="Second agent (Player 2)")
    
    # Match Settings
    parser.add_argument('--games', type=int, default=DEFAULT_NUM_GAMES, help="Number of games to play")
    parser.add_argument('--depth', type=int, default=DEFAULT_DEPTH_LIMIT, help="Depth limit for agents")
    parser.add_argument('--time', type=float, default=DEFAULT_TIME_LIMIT, help="Time limit (seconds) per move")
    parser.add_argument('--elo', type=int, default=DEFAULT_STOCKFISH_ELO, help="Elo for Stockfish (if used)")
    
    args = parser.parse_args()

    print(f"--- STARTING MATCH: {args.agent1.title()} vs {args.agent2.title()} ---")
    print(f"Settings: {args.games} Games | Time: {args.time}s | Depth: {args.depth} | SF Elo: {args.elo}")
    
    match_data = []
    p1_wins = 0
    p2_wins = 0
    draws = 0
    start_time = time.time()

    for i in range(args.games):
        # Alternate who plays white
        p1_plays_white = (i % 2 == 0)
        
        try:
            data = play_game(i, args.agent1, args.agent2, p1_plays_white, args)
            match_data.append(data)

            if data["Winner"] == args.agent1.title():
                p1_wins += 1
            elif data["Winner"] == args.agent2.title():
                p2_wins += 1
            else:
                draws += 1
                
        except Exception as e:
            print(f"CRASH in Game {i+1}: {e}")
            continue

    total_time = time.time() - start_time
    
    print("\n================ MATCH RESULTS ================")
    print(f"Total Games: {args.games}")
    print(f"Time Elapsed: {total_time/60:.2f} minutes")
    print("-----------------------------------------------")
    print(f"{args.agent1.title()} Wins: {p1_wins} ({p1_wins/args.games*100:.1f}%)")
    print(f"{args.agent2.title()} Wins: {p2_wins} ({p2_wins/args.games*100:.1f}%)")
    print(f"Draws:          {draws} ({draws/args.games*100:.1f}%)")
    print("===============================================")

    df = pd.DataFrame(match_data)
    if not os.path.exists(PLOT_FOLDER): os.makedirs(PLOT_FOLDER)
    df.to_csv(os.path.join(PLOT_FOLDER, "match_results.csv"), index=False)
    
    generate_plots(df, args.agent1, args.agent2)

if __name__ == "__main__":
    main()