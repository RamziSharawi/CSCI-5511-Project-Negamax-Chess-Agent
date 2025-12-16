<img src="./RepoLogo.png" width="48">

# 🌟 Motivation
The use of artificial intelligence (AI) in chess has been a subject of intense research since the 1950s, when Alan Turing was the first to develop a theoretical chess-playing program in 1951. Ever since then, progress in AI-based chess agents has advanced significantly, with modern data-driven chess engines including AlphaZero and its open-source alternative, Leela Chess Zero. Such modern chess engines typically integrate deep reinforcement learning techniques to enhance decision-making within Monte-Carlo Tree Search (MCTS). By leveraging an abundance of chess data and top-tier computational resources, modern chess engines have achieved superhuman chess abilities, transforming how the game is studied and analyzed today.

Despite the strength of modern chess engines like AlphaZero and Leela Chess Zero, they require intense computational resources and time for self-play training, often requiring TPUs/GPUs to play out millions of games. To address this computational bottleneck, this paper proposes RAM-Z: an optimized chess agent built upon classical AI methods. By framing the game as a minimax problem, a Negamax search framework is employed and enhanced with Alpha-Beta pruning and Iterative Deepening to efficiently navigate the state space. To further tackle the large average branching factor per turn, techniques such as iterative deepening, move reordering, transposition tables, and null-move pruning were also integrated into the developed chess agent, helping to avoid redundant searches and to optimize the pruning process. Furthermore, quiescence search was incorporated for the agent to circumvent the horizon effect in depth-limited search spaces. By integrating these techniques into the developed RAM-Z chess agent, this paper aims to benchmark the agent's tactical limits on standard hardware, offering a lightweight alternative to the resource-intensive pipelines of modern neural-network-based engines.

**This project was completed towards the requirements of my CSCI-5511: Artificial Intelligence I course at the University of Minnesota, Twin Cities, in Fall 2025.**

# ✨ Introduction
All aspects of this codebase are implemented in **Python 3.10.10**, chosen for its readability and extensive library support. The core game mechanics are handled by the **python-chess** library, which provides a robust framework for move generation, move validation, and board representation. This library utilizes efficient bitboard operations (integer-based board mapping), allowing the agent to query piece locations and attack masks with minimal computational overhead. To aid with user interaction, the engine is coupled with a custom Graphical User Interface (GUI) developed using the **Pygame** library, displaying the chess board and allowing the user to play against all agents in this repository. The RAM-Z chess agent implements the following techniques to optimize its search process:

1. **Negamax Search Algorithm:** A variant of Minimax that simplifies the implementation by relying on the zero-sum property of chess, reducing code complexity while maintaining identical behavior to Minimax.
2. **Alpha-Beta Pruning:** An optimization applied to the search that significantly reduces the number of nodes evaluated by safely ignoring branches that cannot influence the final decision.
3. **Opening Book Integration:** To ensure robust play in the opening, the RAM-Z utilizes the **gm2600.bin** opening book, allowing for instant, high-quality move lookup during the initial phase.
4. **Heuristic Evaluation:** The agent evaluates board states using a custom evaluation function based on PeSTO piece-square tables to assess position strength beyond the search horizon.


# 🚀 Getting Started

## Installation
To clone this repository:

```bash
git clone https://github.com/RamziSharawi/CSCI-5511-Project-Negamax-Chess-Agent.git
```

## Environment Set Up
You can set up the environment using either Conda or Python's built-in `venv` module. Choose the option that works best for you. If you didn't already, after cloning the GitHub repository, make sure to set the folder as your current working location:
```bash
cd CSCI-5511-Project-Negamax-Chess-Agent
```

### Option 1: Using Conda
```bash
conda create -n RAMZAgent python=3.10
conda activate RAMZAgent
pip install -r requirements.txt
```

### Option 2: Using venv

**1. Create the virtual environment:**
```bash
python -m venv RAMZAgent
```

**2. Activate the virtual environment:**
  * Windows:
  ```bash
  .\RAMZAgent\Scripts\activate
  ```
  * Mac/Linux:
  ```bash
  source RAMZAgent/bin/activate
  ```
**3. Install the dependencies:**
```bash
pip install -r requirements.txt
```

# 🖥️ Usage Instructions
This repository contains three main files:
1. **players.py:** Contains all agents used in the codebase. This includes a RandomPlayer agent (plays random moves), a RAMZPlayer agent (the RAM-Z chess agent), and a StockfishPlayer agent (standard Stockfish).
2. **chess_gui.py:** Contains code to play against any of the included agents using a chessboard GUI. 
3. **win_ratio.py** Plays specified agents against each other to analyze their performances against each other.

The only files that need to be run are **chess_gui.py** and **win_ratio.py**. Instructions on how to run them through the terminal are below.

### Playing against agents
To launch the GUI and play a game against a certain agent, run the **chess_gui.py** script from your terminal.
**Example Command:**
```bash
python chess_gui.py --color black --agent ramz --depth 10 --time 1.0 --elo 1500
```
Command-line arguments:
 * **--color**: Sets your opponent's starting color (`white` or `black`). Default is `black`.
 * **--agent**: Sets the agent to play as your opponent (`random`, `ramz`, `stockfish`). Default is `ramz`.
 * **--depth**: Sets the maximum search depth for the agent (in plies). Default is `4`.
 * **--time**: Sets the time limit per move for the agent (in seconds). Default is `5.0`.
 * **--elo**: Sets the approximate ELO rating for the agent (only supported by Stockfish). Default is `1500`.

### Evaluating agent performances
To play agents against each other and obtain their win-ratios and plots on performance by starting color and game phase, run the **win_ratio.py** script from your terminal.
**Example Command:**
```bash
python win_ratio.py --agent1 ramz --agent2 stockfish --games 100 --depth 4 --time 5.0 --elo 1500
```
Command-line arguments:
 * **--agent1**: Sets the agent to play as White (`random`, `ramz`, `stockfish`). Default is `ramz`.
 * **--agent2**: Sets the agent to play as Black (`random`, `ramz`, `stockfish`). Default is `stockfish`.
 * **--games**: Number of games to play. Default is `100`.
 * **--depth**: Sets the maximum search depth for the agent (in plies). Default is `4`.
 * **--time**: Sets the time limit per move for the agent (in seconds). Default is `5.0`.
 * **--elo**: Sets the approximate ELO rating for the agent (only supported by Stockfish). Default is `1500`.



