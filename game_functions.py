import chess

def player(board):
    if board.turn == False:
        color = "WHITE"
    else:
        color = "BLACK"
    return color

def actions(board):
    '''Return a list of possible actions given the current board state
    '''
    legal_actions = []
    for m in board.legal_moves:
        legal_actions.append(m)
    return legal_actions

def result(board, current_square, next_square):
    '''Returns the resulting state after taking the given action

    (This is the workhorse function for checking legal moves as well as making moves)

    If the given action is not legal, returns None

    '''
    move = chess.Move(from_square = current_square, to_square = next_square)
    board.push(move)

    return board