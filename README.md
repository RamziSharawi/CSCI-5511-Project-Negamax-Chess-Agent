![Negamax Chess Agent Logo](./RepoLogo.png)
# 🌟 Motivation
The use of artificial intelligence (AI) in chess has been a subject of intense research since the 1950s, when Alan Turing was the first to develop a theoretical chess-playing program in 1951. Ever since then, progress in AI-based chess agents has advanced significantly, with modern data-driven chess engines including AlphaZero and its open-source alternative, Leela Chess Zero. Such modern chess engines typically integrate deep reinforcement learning techniques to enhance decision-making within Monte-Carlo Tree Search (MCTS). By leveraging an abundance of chess data and top-tier computational resources, modern chess engines have achieved superhuman chess abilities, transforming how the game is studied and analyzed today.

Despite the strength of modern chess engines like AlphaZero and Leela Chess Zero, they require intense computational resources and time for self-play training, often requiring TPUs/GPUs to play out millions of games. To address this computational bottleneck, this paper proposes RAM-Z: an optimized chess agent built upon classical AI methods. By framing the game as a minimax problem, a Negamax search framework is employed and enhanced with Alpha-Beta pruning and Iterative Deepening to efficiently navigate the state space. To further tackle the large average branching factor per turn, techniques such as iterative deepening, move reordering, transposition tables, and null-move pruning were also integrated into the developed chess agent, helping to avoid redundant searches and to optimize the pruning process. Furthermore, quiescence search was incorporated for the agent to circumvent the horizon effect in depth-limited search spaces. By integrating these techniques into the developed RAM-Z chess agent, this paper aims to benchmark the agent's tactical limits on standard hardware, offering a lightweight alternative to the resource-intensive pipelines of modern neural-network-based engines.

This project was completed towards the requirements of my CSCI-5511: Artificial Intelligence I course at the University of Minnesota, Twin Cities, in Fall 2025.

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
Install required packages:

```bash
conda create -n RAMZAgent python=3.10
conda activate RAMZAgent
pip install -r requirements.txt
```

