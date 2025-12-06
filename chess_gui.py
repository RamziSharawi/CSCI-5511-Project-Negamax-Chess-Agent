import chess
import pygame
from players import RandomPlayer, AdvancedPlayer
### FUNCTION DEFINITIONS
# --- Draws the chess board ---
def draw_board():
    for r in range(8):
        for c in range(8):
            color = LIGHT if (r + c) % 2 == 0 else DARK
            pygame.draw.rect(screen, color, pygame.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

# --- Draws chess pieces ---
def draw_pieces(board_obj, dragging_piece_pos=None):
    for square, piece in board_obj.piece_map().items():
        if selected_square is not None and square == selected_square:
            continue  # skip drawing dragging piece
        col = chess.square_file(square)
        row = 7 - chess.square_rank(square)
        color = "w" if piece.color else "b"
        piece_name = color + piece.symbol().lower()
        screen.blit(PIECES[piece_name], (col*SQ_SIZE, (row)*SQ_SIZE))

    # draw dragging piece on top
    if dragging_piece and dragging_piece_pos:
        screen.blit(dragging_piece, (dragging_piece_pos[0] - SQ_SIZE//2, dragging_piece_pos[1] - SQ_SIZE//2))

def draw_highlights(squares):
    s = pygame.Surface((SQ_SIZE, SQ_SIZE), pygame.SRCALPHA)
    s.fill(HIGHLIGHT_COLOR)
    for sq in squares:
        col = chess.square_file(sq)
        row = 7 - chess.square_rank(sq)
        screen.blit(s, (col*SQ_SIZE, (row)*SQ_SIZE))

# --- Returns square selected by mouse ---
def square_from_mouse(pos):
    x, y = pos
    col = x // SQ_SIZE
    row = 7 - (y // SQ_SIZE)
    return chess.square(col, row)

def draw_game_over(winner):
    # Semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)  # transparency 0-255
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    # Game over text
    font_large = pygame.font.SysFont("Arial", 64, bold=True)
    text = font_large.render(f"Game Over! {winner} wins", True, (255, 255, 255))
    text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(text, text_rect)

### MAIN SCRIPT

# Player definition
AIColor = chess.WHITE
HumanColor = chess.BLACK
Player = AdvancedPlayer(AIColor, depth_limit = 4, time_limit = 5.0, opening_book_path="opening_books/gm2600.bin", syzygy_path=None)
# Setting parameter values
WIDTH, HEIGHT = 640, 640
SQ_SIZE = WIDTH//8
LIGHT, DARK = (240, 217, 181), (181, 136, 99)
HIGHLIGHT_COLOR = (186, 202, 68, 100)  # translucent green

# Initializing game environment
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CSCI-5511 Chess Project")

# Initializing chess board from python-chess
board = chess.Board()
PIECES = {} # Empty pieces dictionary
for piece in ["wp", "wr", "wn", "wb", "wk", "wq", "bp", "br", "bn", "bb", "bk", "bq"]:
    image = pygame.image.load(f"pieces/{piece}.png")
    PIECES[piece] = pygame.transform.smoothscale(image, (SQ_SIZE, SQ_SIZE))

selected_square = None
dragging_piece = None
legal_moves = []
dragging_piece_pos = None
running = True
game_over = False
while running:
    if board.is_game_over() and not game_over:
        game_over = True
        result = board.result()
        if result == "1-0":
            winner = "WHITE"
        elif result == "0-1":
            winner = "BLACK"
        else:
            winner = "DRAW"

    if not game_over and board.turn == AIColor:
        draw_board()
        draw_pieces(board)
        
        # Optional: small delay so the AI doesn't move instantly (easier to follow)
        pygame.time.wait(500)

        ai_move = Player.make_move(board)
        board.push(ai_move)

        continue

    # --- HANDLING HUMAN INPUT
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            square = square_from_mouse(event.pos)
            print(f"Clicked square: {chess.square_name(square)}") # Add this!
            piece = board.piece_at(square)

            if piece and piece.color == HumanColor:
                selected_square = square
                dragging_piece = PIECES[("w" if piece.color else "b") + piece.symbol().lower()]
                # highlight legal moves
                legal_moves = [m.to_square for m in board.legal_moves if m.from_square == square]
                dragging_piece_pos = event.pos
        elif event.type == pygame.MOUSEMOTION and selected_square:
            dragging_piece_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP and selected_square:
            release_square = square_from_mouse(event.pos)
            move = chess.Move(selected_square, release_square)
            if move in board.legal_moves:
                board.push(move)
            elif chess.Move(selected_square, release_square, promotion=chess.QUEEN) in board.legal_moves:
                     board.push(chess.Move(selected_square, release_square, promotion=chess.QUEEN))
            # reset drag
            selected_square = None
            dragging_piece = None
            legal_moves = []
            dragging_piece_pos = None

    draw_board()
    draw_highlights(legal_moves)
    draw_pieces(board, dragging_piece_pos)
    if game_over:
        draw_game_over(winner)
    pygame.display.flip()

pygame.quit()