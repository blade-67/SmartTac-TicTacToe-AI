import math
import random
from constants import *

# --- Check for win ---
def check_winner(board):
    # Check all directions: horizontal, vertical, diagonal
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col]:
                for dr, dc in directions:
                    count = 1
                    mark = board[row][col]
                    
                    # Check in positive direction
                    r, c = row + dr, col + dc
                    while (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and 
                           board[r][c] == mark):
                        count += 1
                        r, c = r + dr, c + dc
                    
                    # Check in negative direction
                    r, c = row - dr, col - dc
                    while (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and 
                           board[r][c] == mark):
                        count += 1
                        r, c = r - dr, c - dc
                    
                    if count >= 4:  # Win condition: 4 in a row
                        return mark
    return None

# --- Check available moves ---
def available_moves(board):
    return [(i, j) for i in range(BOARD_SIZE) for j in range(BOARD_SIZE) if board[i][j] is None]

# --- Heuristic Evaluation (for large boards) ---
def evaluate(board):
    score = 0
    # Check all directions
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col]:
                for dr, dc in directions:
                    # Look for sequences
                    count = 1
                    mark = board[row][col]
                    empty_ends = 0
                    
                    # Check forward
                    r, c = row + dr, col + dc
                    while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                        if board[r][c] == mark:
                            count += 1
                        elif board[r][c] is None:
                            empty_ends += 1
                            break
                        else:
                            break
                        r, c = r + dr, c + dc
                    
                    # Check backward
                    r, c = row - dr, col - dc
                    while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                        if board[r][c] == mark:
                            count += 1
                        elif board[r][c] is None:
                            empty_ends += 1
                            break
                        else:
                            break
                        r, c = r - dr, c - dc
                    
                    # Score the sequence
                    if mark == AI:
                        if count >= 4:
                            score += 100  # Winning move
                        elif count == 3 and empty_ends >= 1:
                            score += 5   # Three in a row with space
                        elif count == 2 and empty_ends == 2:
                            score += 2   # Two in a row with spaces
                    elif mark == PLAYER:
                        if count >= 4:
                            score -= 100  # Block player's win
                        elif count == 3 and empty_ends >= 1:
                            score -= 10   # Block three in a row
                        elif count == 2 and empty_ends == 2:
                            score -= 2    # Block two in a row
    
    # Add position-based scoring
    center_rows = [2, 3]
    center_cols = [2, 3]
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == AI:
                if row in center_rows and col in center_cols:
                    score += 3  # Center positions
                elif row in center_rows or col in center_cols:
                    score += 2  # Semi-center positions
                else:
                    score += 1  # Edge positions
    
    return score

# --- Minimax Algorithm ---
def minimax(board, depth, is_maximizing, alpha, beta):
    winner = check_winner(board)
    if winner == AI:
        return 10
    elif winner == PLAYER:
        return -10
    elif not available_moves(board) or depth == 0:
        return evaluate(board)

    if is_maximizing:
        max_eval = -math.inf
        for (i, j) in available_moves(board):
            board[i][j] = AI
            eval = minimax(board, depth - 1, False, alpha, beta)
            board[i][j] = None
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = math.inf
        for (i, j) in available_moves(board):
            board[i][j] = PLAYER
            eval = minimax(board, depth - 1, True, alpha, beta)
            board[i][j] = None
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

# --- Best Move ---
def best_move(board):
    best_val = -math.inf
    moves = []
    
    # Check for immediate winning move
    for (i, j) in available_moves(board):
        board[i][j] = AI
        if check_winner(board) == AI:
            board[i][j] = None
            return (i, j)
        board[i][j] = None
    
    # Check for immediate blocking move
    for (i, j) in available_moves(board):
        board[i][j] = PLAYER
        if check_winner(board) == PLAYER:
            board[i][j] = None
            return (i, j)
        board[i][j] = None
    
    # If no immediate win/block, use minimax
    for (i, j) in available_moves(board):
        board[i][j] = AI
        move_val = minimax(board, 3, False, -math.inf, math.inf)
        board[i][j] = None
        if move_val > best_val:
            best_val = move_val
            moves = [(i, j)]
        elif move_val == best_val:
            moves.append((i, j))
    
    # Return a random move from the best moves
    return random.choice(moves) if moves else None
