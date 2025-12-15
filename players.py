import chess
import chess.polyglot
import random
from game_functions import actions
import chess.syzygy
import time
import chess.engine

# Based on PeSTO evaluation function. First element of tuple is midgame value, second is endgame value.
MATERIAL_PESTO = {
    chess.PAWN:   (82, 94),
    chess.KNIGHT: (337, 281),
    chess.BISHOP: (365, 297),
    chess.ROOK:   (477, 512),
    chess.QUEEN:  (1025, 936),
    chess.KING:   (0, 0)
}

PAWN_MG = [
      0,   0,   0,   0,   0,   0,   0,   0,
     98, 134,  61,  95,  68, 126,  34, -11,
     -6,   7,  26,  31,  65,  56,  25, -20,
    -14,  13,   6,  21,  23,  12,  17, -23,
    -27,  -2,  -5,  12,  17,   6,  10, -25,
    -26,  -4,  -4, -10,   3,   3,  33, -12,
    -35,  -1, -20, -23, -15,  24,  38, -22,
      0,   0,   0,   0,   0,   0,   0,   0
]

KNIGHT_MG = [
   -167, -89, -34, -49,  61, -97, -15, -107,
    -73, -41,  72,  36,  23,  62,   7,  -17,
    -47,  60,  37,  65,  84, 129,  73,   44,
     -9,  17,  19,  53,  37,  69,  18,   22,
    -13,   4,  16,  13,  28,  19,  21,   -8,
    -23,  -9,  12,  10,  19,  17,  25,  -16,
    -29, -53, -12,  -3,  -1,  18, -14,  -19,
   -105, -21, -58, -33, -17, -28, -19,  -23
]

BISHOP_MG = [
    -29,   4, -82, -37, -25, -42,   7,  -8,
    -26,  16, -18, -13,  30,  59,  18, -47,
    -16,  37,  43,  40,  35,  50,  37,  -2,
     -4,   5,  19,  50,  37,  37,   7,  -2,
     -6,  13,  13,  26,  34,  12,  10,   4,
      0,  15,  15,  15,  14,  27,  18,  10,
      4,  15,  16,   0,   7,  21,  33,   1,
    -33,  -3, -14, -21, -13, -12, -39, -21
]

ROOK_MG = [
     32,  42,  32,  51,  63,   9,  31,  43,
     27,  32,  58,  62,  80,  67,  26,  44,
     -5,  19,  26,  36,  17,  45,  61,  16,
    -24, -11,   7,  26,  24,  35,  -8, -20,
    -36, -26, -12,  -1,   9,  -7,   6, -23,
    -45, -25, -16, -17,   3,   0,  -5, -33,
    -44, -16, -20,  -9,  -1,  11,  -6, -71,
    -19, -13,   1,  17,  16,   7, -37, -26
]

QUEEN_MG = [
    -28,   0,  29,  12,  59,  44,  43,  45,
    -24, -39,  -5,   1, -16,  57,  28,  54,
    -13, -17,   7,   8,  29,  56,  47,  57,
    -27, -27, -16, -16,  -1,  17,  -2,   1,
     -9, -26,  -9, -10,  -2,  -4,   3,  -3,
    -14,   2, -11,  -2,  -5,   2,  14,   5,
    -35,  -8,  11,   2,   8,  15,  -3,   1,
     -1, -18,  -9,  10, -15, -25, -31, -50
]

KING_MG = [
    -65,  23,  16, -15, -56, -34,   2,  13,
     29,  -1, -20,  -7,  -8,  -4, -38, -29,
     -9,  24,   2, -16, -20,   6,  22, -22,
    -17, -20, -12, -27, -30, -25, -14, -36,
    -49,  -1, -27, -39, -46, -44, -33, -51,
    -14, -14, -22, -46, -44, -30, -15, -27,
      1,   7,  -8, -64, -43, -16,   9,   8,
    -15,  36,  12, -54,   8, -28,  24,  14
]

# --- ENDGAME TABLES (EG) ---
PAWN_EG = [
      0,   0,   0,   0,   0,   0,   0,   0,
    178, 173, 158, 134, 147, 132, 165, 187,
     94, 100,  85,  67,  56,  53,  82,  84,
     32,  24,  13,   5,  -2,   4,  17,  17,
     13,   9,  -3,  -7,  -7,  -8,   3,  -1,
      4,   7,  -6,   1,   0,  -5,  -1,  -8,
     13,   8,   8,  10,  13,   0,   2,  -7,
      0,   0,   0,   0,   0,   0,   0,   0
]

KNIGHT_EG = [
    -58, -38, -13, -28, -31, -27, -63, -99,
    -25,  -8, -25,  -2,  -9, -25, -24, -52,
    -24, -20,  10,   9,  -1,  -9, -19, -41,
    -17,   3,  22,  22,  22,  11,   8, -18,
    -18,  -6,  16,  25,  16,  17,   4, -18,
    -23,  -3,  -1,  15,  10,  -3, -20, -22,
    -42, -20, -10,  -5,  -2, -20, -23, -44,
    -29, -51, -23, -15, -22, -18, -50, -64
]

BISHOP_EG = [
    -14, -21, -11,  -8, -7,  -9, -17, -24,
     -8,  -4,   7, -12, -3, -13,  -4, -14,
      2,  -8,   0,  -1, -2,   6,   0,   4,
     -3,   9,  12,   9, 14,  10,   3,   2,
     -6,   3,  13,  19,  7,  10,  -3,  -9,
    -12,  -3,   8,  10, 13,   3,  -7, -15,
    -14, -18,  -7,  -1,  4,  -9, -15, -27,
    -23,  -9, -23,  -5, -9, -16,  -5, -17
]

ROOK_EG = [
     13,  10,  18,  15,  12,  12,   8,   5,
     11,  13,  13,  11, -12,  11,  12,  16,
      7,   7,   7,   5,   4,  -3,  -5,  -3,
      4,   3,  13,   1,   2,   1,  -1,   2,
      3,   5,   8,   4,  -5,  -6,  -8, -11,
     -4,   0,  -5,  -1,  -7, -12,  -8, -16,
     -6,  -6,   0,   2,  -9,  -9, -11,  -3,
     -9,   2,   3,  -1,  -5, -13,   4, -20
]

QUEEN_EG = [
     -9,  22,  22,  27,  27,  19,  10,  20,
    -17,  20,  32,  41,  58,  25,  30,   0,
    -20,   6,   9,  49,  47,  35,  19,   9,
      3,  22,  24,  45,  43,  40,  36,  -6,
    -18,  28,  19,  47,  31,  34,  39,  23,
    -16, -27,  15,   6,   9,  17,  10,   5,
    -22, -23, -30, -16, -16, -23, -36, -32,
    -33, -28, -22, -43,  -5, -32, -20, -41
]

KING_EG = [
    -74, -35, -18, -18, -11,  15,   4, -17,
    -12,  17,  14,  17,  17,  38,  23,  11,
     10,  17,  23,  15,  20,  45,  44,  13,
     -8,  22,  24,  27,  26,  33,  26,   3,
    -18,  -4,  21,  24,  27,  23,   9, -11,
    -19,  -3,  11,  21,  23,  16,   7,  -9,
    -27, -11,   4,  13,  14,   4,  -5, -17,
    -53, -34, -21, -11, -28, -14, -24, -43
]

PST_DICT_MG = {
    chess.PAWN: PAWN_MG, chess.KNIGHT: KNIGHT_MG, chess.BISHOP: BISHOP_MG,
    chess.ROOK: ROOK_MG, chess.QUEEN: QUEEN_MG,   chess.KING: KING_MG
}
PST_DICT_EG = {
    chess.PAWN: PAWN_EG, chess.KNIGHT: KNIGHT_EG, chess.BISHOP: BISHOP_EG,
    chess.ROOK: ROOK_EG, chess.QUEEN: QUEEN_EG,   chess.KING: KING_EG
}

class RandomPlayer():
    def __init__(self, mycolor):
        self.color = mycolor
    
    def get_color(self):
        return self.color
    
    def make_move(self, board):
        legals = actions(board)
        curr_move = random.choice(legals)
        return curr_move

class RAMZPlayer():

    def __init__(self, mycolor, depth_limit, time_limit, opening_book_path, syzygy_path):
        self.mycolor = mycolor
        self.depth_limit = depth_limit
        self.time_limit = time_limit
        self.opening_book_path = opening_book_path
        self.syzygy_path = syzygy_path

        self.transposition_table = {}
        self.history_table = [[[0 for _ in range(64)] for _ in range(64)] for _ in range(2)]
        self.MAX_PLY = 16 # Max search depth (ply)
        # Create a list of [None, None] for each ply
        self.killer_moves = [[None, None] for _ in range(self.MAX_PLY)]
        self.init_pst_tables()


        self.ENTRY_TYPE_EXACT = 0
        self.ENTRY_TYPE_LOWER = 1
        self.ENTRY_TYPE_UPPER = 2

    @staticmethod
    def iter_bits(bitboard):
        """
        Accepts either an int bitboard or a python-chess SquareSet.
        Converts to int and yields square indices (0-63) for 1 bits.
        """
        # Ensure we have an int (SquareSet supports int(SquareSet))
        bb = int(bitboard)
        while bb:
            lsb = bb & -bb
            sq = (lsb.bit_length() - 1)
            yield sq
            bb ^= lsb

    
    def init_pst_tables(self):
        self.PST_MG_WHITE = {pt: [0]*64 for pt in range(1, 7)}
        self.PST_EG_WHITE = {pt: [0]*64 for pt in range(1, 7)}
        self.PST_MG_BLACK = {pt: [0]*64 for pt in range(1, 7)}
        self.PST_EG_BLACK = {pt: [0]*64 for pt in range(1, 7)}

        for pt in range(1, 7):
            mg_list = PST_DICT_MG[pt]
            eg_list = PST_DICT_EG[pt]

            for sq in range(64):
                # White uses it normally
                self.PST_MG_WHITE[pt][sq] = mg_list[sq]
                self.PST_EG_WHITE[pt][sq] = eg_list[sq]

                # BLACK: Uses the "Mirrored" square, since PeSTO tables are from White's perspective
                mirror_sq = chess.square_mirror(sq)
                self.PST_MG_BLACK[pt][sq] = mg_list[mirror_sq]
                self.PST_EG_BLACK[pt][sq] = eg_list[mirror_sq]
        
        self.PASSED_PAWN_MASK = {chess.WHITE: [0]*64, chess.BLACK: [0]*64}

        for sq in range(64):
            file = chess.square_file(sq)
            rank = chess.square_rank(sq)
            
            # WHITE MASK: Squares in front of the pawn
            w_mask = 0
            for r in range(rank + 1, 8):
                for f in range(max(0, file - 1), min(8, file + 2)):
                    w_mask |= (1 << (r * 8 + f))
            self.PASSED_PAWN_MASK[chess.WHITE][sq] = w_mask

            # BLACK MASK: Squares in front of the pawn (mirrored direction)
            b_mask = 0
            for r in range(0, rank):
                for f in range(max(0, file - 1), min(8, file + 2)):
                    b_mask |= (1 << (r * 8 + f))
            self.PASSED_PAWN_MASK[chess.BLACK][sq] = b_mask

    def get_color(self):
        return self.mycolor

    def make_move(self, board, time_limit=10.0):
        # 1. Opening Book
        if self.opening_book_path:
            try:
                with chess.polyglot.open_reader(self.opening_book_path) as reader:
                    # Optional: Check if we actually have moves
                    if sum(1 for _ in reader.find_all(board)) > 0:
                        return reader.weighted_choice(board).move
            except Exception as e:
                print(f"OPENING BOOK ERROR: {e}")
                pass

        # 2. Reset Tables
        if len(self.transposition_table) > 1000000:
            self.transposition_table.clear()
            print("TT cleared due to size limit.")
        self.killer_moves = [[None, None] for _ in range(self.MAX_PLY)]
        # Reset history heuristic (divide by 2 to decay old values)
        for c in range(2):
            for f in range(64):
                for t in range(64):
                    self.history_table[c][f][t] //= 2

        best_move_so_far = None
        start_time = time.time()
        
        # 3. Iterative Deepening
        # We try Depth 1, then Depth 2, then Depth 3...
        # We stop ONLY when we run out of time.
        for current_depth in range(1, self.depth_limit): # 100 is effectively infinite
            
            # CHECK TIME: If we used more than 50% of our time, stop.
            # (Because the next depth will likely take longer than the remaining 50%)
            if (time.time() - start_time) > (self.time_limit/3.5):
                break

            try:
                # Search
                score, move = self.negamax(board, float("-inf"), float("inf"), current_depth, 0)
                
                # Update best move
                best_move_so_far = move
                
                # Print info (optional)
                elapsed = time.time() - start_time
                #print(f"Depth {current_depth} | Score: {score} | Time: {elapsed:.2f}s")

                if score > 90000000:
                    #print("Checkmate found! Stopping search early.")
                    break

            except Exception as e:
                print(f"Error at depth {current_depth}: {e}")
                break
        
        return best_move_so_far

    def order_moves(self, board, tt_best_move, killers):
        VICTIM_VALUES = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}
        killer1, killer2 = killers
        
        # Fast lists
        captures = []
        quiet_killers = []
        quiet_history = []
        quiet_others = []

        for move in board.legal_moves:
            if move == tt_best_move:
                yield move
                continue

            if board.is_capture(move):
                # Fast MVV-LVA
                victim = board.piece_at(move.to_square)
                val = VICTIM_VALUES.get(victim.piece_type, 0) if victim else 1 # En passant = 1
                captures.append((val, move))
            
            elif move == killer1:
                quiet_killers.append((2, move))
            elif move == killer2:
                quiet_killers.append((1, move))
            else:
                # History Heuristic
                h_score = self.history_table[int(board.turn)][move.from_square][move.to_square]
                quiet_history.append((h_score, move))

        # Sort and Yield
        # 1. Captures (High val first)
        captures.sort(key=lambda x: x[0], reverse=True)
        for _, m in captures: yield m
        
        # 2. Killers
        quiet_killers.sort(key=lambda x: x[0], reverse=True)
        for _, m in quiet_killers: yield m
        
        # 3. History
        quiet_history.sort(key=lambda x: x[0], reverse=True)
        for _, m in quiet_history: yield m

    
    def negamax(self, board, alpha, beta, depth_remaining, ply):

        original_alpha = alpha
        zobrist_key = chess.polyglot.zobrist_hash(board)
        if zobrist_key in self.transposition_table:
            entry = self.transposition_table[zobrist_key]
            
            if entry['depth'] >= depth_remaining:
                if entry['flag'] == self.ENTRY_TYPE_EXACT:
                    return entry['score'], entry['best_move']
                elif entry['flag'] == self.ENTRY_TYPE_LOWER:
                    alpha = max(alpha, entry['score']) # Update lower bound
                elif entry['flag'] == self.ENTRY_TYPE_UPPER:
                    beta = min(beta, entry['score'])   # Update upper bound

                # Check for cutoff after updating bounds
                if alpha >= beta:
                    return entry['score'], entry['best_move']

        if board.is_game_over():

            if board.turn == self.mycolor:
                return self.utility(board), None
            else:
                base_score = -self.utility(board)
                if base_score > 90000000:
                    base_score -= ply 
                return base_score, None

        if depth_remaining <= 0:
            return self.quiescence(board, alpha, beta), None

        # # ### NULL MOVE PRUNING ###
        if depth_remaining >= 3 and not board.is_check() and ply > 0:
            # Making the null move (i.e. skipping my turn)
            occupied = board.occupied_co[board.turn]
            kings = int(board.pieces(chess.KING, board.turn))
            pawns = int(board.pieces(chess.PAWN, board.turn))
            
            # 'occupied & ~kings & ~pawns' removes kings and pawns from the count
            has_major_pieces = (occupied & ~kings & ~pawns) != 0
            if has_major_pieces:
                board.push(chess.Move.null())
                R = 2
                score, _ = self.negamax(board, -beta, -beta + 1, depth_remaining - 1 - R, ply + 1)
                board.pop()
                if score >= beta:
                    return beta, None

        v = float("-inf")
        best_move = None

        tt_best_move = None

        if zobrist_key in self.transposition_table:
            # .get() is safer, in case 'best_move' isn't stored
            tt_best_move = self.transposition_table[zobrist_key].get('best_move')

        current_killers = self.killer_moves[ply]

        ordered_moves = self.order_moves(board, tt_best_move, current_killers)
    
        # if tt_best_move in ordered_moves:
        #     ordered_moves.remove(tt_best_move)
        #     ordered_moves.insert(0, tt_best_move)

        for move in ordered_moves:
            board.push(move)

            v2_opponent, _ = self.negamax(board, -beta, -alpha, depth_remaining-1, ply + 1)
            v2 = -v2_opponent

            board.pop()

            if v2 > v:
                v = v2
                best_move = move
                alpha = max(alpha, v)
            
            if v >= beta:
                if not board.is_capture(move) and not move.promotion:
                    if move != self.killer_moves[ply][0]:
                        self.killer_moves[ply][1] = self.killer_moves[ply][0] # Shift old
                        self.killer_moves[ply][0] = move                     # Add new
                    # Get the color of the player *who just moved*
                    color_index = 0 if board.turn == chess.WHITE else 1
                    reward = depth_remaining * depth_remaining
                    self.history_table[color_index][move.from_square][move.to_square] += reward
                
                break # This is your existing beta-cutof

        if v <= original_alpha:
            flag = self.ENTRY_TYPE_UPPER # Failed low
        elif v >= beta:
            flag = self.ENTRY_TYPE_LOWER # Failed high
        else:
            flag = self.ENTRY_TYPE_EXACT # Exact score
            
        entry = {
            'score': v,
            'depth': depth_remaining,
            'flag': flag,
            'best_move': best_move
        }
        self.transposition_table[zobrist_key] = entry
        return v, best_move

    def quiescence(self, board, alpha, beta):
        # 1. Stand-pat (Don't capture if you are already winning)
        stand_pat = self.utility(board)
        if board.turn != self.mycolor:
            stand_pat = -stand_pat

        if stand_pat >= beta:
            return stand_pat

        # === DELTA PRUNING ===
        BIG_DELTA = 1050 # 900 (Queen) + 150 (Safety buffer)
        pawns = board.pieces(chess.PAWN, board.turn)
        if board.turn == chess.WHITE:
            promoters = pawns & chess.BB_RANK_7
        else:
            promoters = pawns & chess.BB_RANK_2
        
        # If we are NOT promoting, we can try to prune
        # If promoters is not 0, we have a dangerous pawn and must search
        if not promoters: 
            if stand_pat < alpha - BIG_DELTA:
                return alpha

        if alpha < stand_pat:
            alpha = stand_pat

        # 2. Search only Captures and Promotions
        captures = [
            m for m in board.legal_moves 
            if board.is_capture(m) or m.promotion
        ]
        
        # Simple MVV-LVA sorting for Q-Search
        VICTIM_VALUES = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}
        def cap_score(move):
            victim = board.piece_at(move.to_square)
            if victim: return VICTIM_VALUES.get(victim.piece_type, 0)
            return 0
            
        captures.sort(key=cap_score, reverse=True)

        for move in captures:
            board.push(move)
            score = -self.quiescence(board, -beta, -alpha)
            board.pop()

            if score >= beta:
                return beta
            if score > alpha:
                alpha = score

        return alpha

    def utility(self, board):
    # Terminal nodes
        if board.is_checkmate():
            return -99999999 if board.turn == self.mycolor else 99999999

        if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_draw():
            return 0

        # --- 1. GAME PHASE CALCULATION ---
        phase = 0
        phase += len(board.pieces(chess.KNIGHT, chess.WHITE)) * 1
        phase += len(board.pieces(chess.KNIGHT, chess.BLACK)) * 1
        phase += len(board.pieces(chess.BISHOP, chess.WHITE)) * 1
        phase += len(board.pieces(chess.BISHOP, chess.BLACK)) * 1
        phase += len(board.pieces(chess.ROOK, chess.WHITE)) * 2
        phase += len(board.pieces(chess.ROOK, chess.BLACK)) * 2
        phase += len(board.pieces(chess.QUEEN, chess.WHITE)) * 4
        phase += len(board.pieces(chess.QUEEN, chess.BLACK)) * 4
        phase = min(phase, 24) 

        mg_score = 0
        eg_score = 0

        # ### NEW: Pre-fetch pawn bitboards as integers for fast bitwise math
        white_pawns_int = int(board.pieces(chess.PAWN, chess.WHITE))
        black_pawns_int = int(board.pieces(chess.PAWN, chess.BLACK))

        # ### NEW: Define bonuses
        PASSED_MG = 20  # Small bonus in middlegame
        PASSED_EG = 50  # Big bonus in endgame (passed pawns are dangerous!)
        
        # --- 2. SUMMATION ---
        for pt in range(1, 7):
            # We get material values from our new tuple dictionary
            mg_val, eg_val = MATERIAL_PESTO[pt]

            # WHITE
            bb_w = board.pieces(pt, chess.WHITE)
            for sq in self.iter_bits(bb_w):
                mg_score += mg_val + self.PST_MG_WHITE[pt][sq]
                eg_score += eg_val + self.PST_EG_WHITE[pt][sq]

                # ### NEW: Passed Pawn Check for White
                if pt == chess.PAWN:
                    if (self.PASSED_PAWN_MASK[chess.WHITE][sq] & black_pawns_int) == 0:
                        rank = chess.square_rank(sq)
                        # Scale bonus by rank (closer to 8 = better)
                        # Rank 0-7. We want high bonus for 4, 5, 6.
                        w_bonus = PASSED_EG + (rank * 10) 
                        
                        mg_score += PASSED_MG
                        eg_score += w_bonus

            # BLACK
            bb_b = board.pieces(pt, chess.BLACK)
            for sq in self.iter_bits(bb_b):
                mg_score -= mg_val + self.PST_MG_BLACK[pt][sq]
                eg_score -= eg_val + self.PST_EG_BLACK[pt][sq]

                if pt == chess.PAWN:
                    if (self.PASSED_PAWN_MASK[chess.BLACK][sq] & white_pawns_int) == 0:
                        # Invert rank for Black (Rank 6 is index 1, Rank 1 is index 6)
                        # python-chess ranks are 0-7 relative to White
                        rank = 7 - chess.square_rank(sq)
                        b_bonus = PASSED_EG + (rank * 10)
                        
                        mg_score -= PASSED_MG
                        eg_score -= b_bonus

                
        
        # --- 3. TAPERED FORMULA (From your C code dump) ---
        # "mgPhase" is just 'phase'
        # "egPhase" is 24 - phase
        final_score = ( (mg_score * phase) + (eg_score * (24 - phase)) ) // 24

        if self.mycolor == chess.WHITE:
            return final_score
        else:
            return -final_score
    
class StockfishPlayer:
    def __init__(self, color, path, depth_limit=4, time_limit=5.0, elo=1500):
        self.color = color
        self.time_limit = time_limit
        self.depth_limit = depth_limit # Store the depth limit
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(path)
            self.engine.configure({"UCI_LimitStrength": True, "UCI_Elo": elo})
        except FileNotFoundError:
            raise FileNotFoundError(f"Could not find Stockfish at: {path}")

    def get_color(self):
        return self.color

    def make_move(self, board):
        limit = chess.engine.Limit(time=self.time_limit, depth=self.depth_limit)
        result = self.engine.play(board, limit)
        return result.move

    def close(self):
        self.engine.quit()
    