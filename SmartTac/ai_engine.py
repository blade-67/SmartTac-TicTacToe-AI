import math
import random
from constants import *
from ai_learning import AILearning

# Initialize AI learning system
ai_learning = AILearning()

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
def analyze_player_strategy(board):
    """Analyze player's strategy based on their moves"""
    player_moves = []
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == PLAYER:
                player_moves.append((row, col))
    
    if not player_moves:
        return None
    
    # Detect patterns in player's moves
    is_playing_center = any(2 <= row <= 3 and 2 <= col <= 3 for row, col in player_moves)
    is_playing_edges = any(row in [0, 5] or col in [0, 5] for row, col in player_moves)
    is_playing_diagonals = any(abs(moves[0][0] - moves[1][0]) == abs(moves[0][1] - moves[1][1]) 
                              for i, moves in enumerate(zip(player_moves[:-1], player_moves[1:])))
    
    return {
        'center_focused': is_playing_center,
        'edge_focused': is_playing_edges,
        'diagonal_focused': is_playing_diagonals,
        'moves': player_moves
    }

def evaluate(board):
    score = 0
    # Check all directions with balanced weights
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    
    # Analyze player's strategy
    player_strategy = analyze_player_strategy(board)
    
    # Function to check if a position is near center
    def is_near_center(row, col):
        return (1 <= row <= 4) and (1 <= col <= 4)
    
    # Function to calculate threat level for any direction
    def calculate_threat(row, col, dr, dc):
        threat_score = 0
        count = 0
        space_before = False
        space_after = False
        mark = board[row][col]
        is_center_line = False
        
        # Check if this is a center line
        if (dr == 0 and 2 <= col <= 3) or (dc == 0 and 2 <= row <= 3):
            is_center_line = True
        
        # Check forward diagonal
        r, c = row, col
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
            if board[r][c] == PLAYER:
                count += 1
            elif board[r][c] is None:
                space_after = True
                break
            else:
                break
            r, c = r + dr, c + dc
        
        # Check backward diagonal
        r, c = row - dr, col - dc
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
            if board[r][c] == PLAYER:
                count += 1
            elif board[r][c] is None:
                space_before = True
                break
            else:
                break
            r, c = r - dr, c - dc
        
        # Calculate threat score
        if count >= 2:
            if space_before and space_after:
                threat_score = 25 if is_near_center(row, col) else 15
            elif space_before or space_after:
                threat_score = 15 if is_near_center(row, col) else 10
        
        return threat_score
    
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col]:
                for dr, dc in directions:
                    # Look for sequences
                    count = 1
                    mark = board[row][col]
                    empty_ends = 0
                    blocked_ends = 0
                    
                    # Check forward
                    r, c = row + dr, col + dc
                    while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                        if board[r][c] == mark:
                            count += 1
                        elif board[r][c] is None:
                            empty_ends += 1
                            break
                        else:
                            blocked_ends += 1
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
                            blocked_ends += 1
                            break
                        r, c = r - dr, c - dc
                        
                    # Give extra weight to vertical alignments in the center columns
                    center_bonus = 1
                    if dr == 1 and dc == 0 and col in [2, 3]:  # Vertical in center
                        center_bonus = 2
                    
                    # Score based on line type and position
                    is_diagonal = abs(dr) == abs(dc) == 1
                    is_horizontal = dr == 0
                    is_vertical = dc == 0
                    
                    # Calculate position-based multiplier
                    pos_multiplier = 1
                    if is_center_line:
                        pos_multiplier = 3
                    elif is_near_center(row, col):
                        pos_multiplier = 2
                    
                    # Direction-based multiplier
                    dir_multiplier = 1
                    if is_diagonal and is_near_center(row, col):
                        dir_multiplier = 1.2
                    elif is_horizontal and 2 <= row <= 3:
                        dir_multiplier = 1.5
                    elif is_vertical and 2 <= col <= 3:
                        dir_multiplier = 1.5
                    
                    if mark == AI:
                        if count >= 4:
                            score += 1000  # Winning move
                        elif count == 3:
                            if empty_ends == 2:  # Open-ended three in a row
                                score += 100 * pos_multiplier * dir_multiplier
                            elif empty_ends == 1:  # Three in a row with one open end
                                score += 50 * pos_multiplier * dir_multiplier
                        elif count == 2:
                            if empty_ends == 2:  # Open-ended two in a row
                                score += 20 * pos_multiplier * dir_multiplier
                            elif empty_ends == 1:  # Two in a row with one open end
                                score += 10 * pos_multiplier * dir_multiplier
                    elif mark == PLAYER:
                        if count >= 4:
                            score -= 1000  # Block player's win
                        elif count == 3:
                            if empty_ends == 2:  # Block open-ended three
                                score -= 200 * pos_multiplier * dir_multiplier
                            elif empty_ends == 1:  # Block three with one open end
                                score -= 100 * pos_multiplier * dir_multiplier
                        elif count == 2:
                            if empty_ends == 2:  # Block open-ended two
                                score -= 40 * pos_multiplier * dir_multiplier
                            elif empty_ends == 1:  # Block two with one open end
                                score -= 20 * pos_multiplier * dir_multiplier
                    
                    # Immediate threat detection for center sequences
                    if mark == PLAYER and is_center_line:
                        if count == 2 and empty_ends >= 1:
                            # Check if the sequence can be extended to win
                            potential_win = False
                            r, c = row + dr * 2, col + dc * 2  # Look two steps ahead
                            if (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and 
                                board[r][c] is None):
                                potential_win = True
                            r, c = row - dr * 2, col - dc * 2  # Look two steps behind
                            if (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and 
                                board[r][c] is None):
                                potential_win = True
                            if potential_win:
                                score -= 200 * center_bonus  # Severe penalty for potential center win
                    
                    # Add penalty for blocked positions, less severe in center
                    if blocked_ends == 2:  # Both ends blocked
                        score -= 2 if is_center_line else 1
    
    # Add position-based scoring with enhanced center control
    center_positions = {
        (2, 2): 8,  # Top-left center
        (2, 3): 8,  # Top-right center
        (3, 2): 8,  # Bottom-left center
        (3, 3): 8   # Bottom-right center
    }
    
    semi_center_rows = [1, 4]  # Rows adjacent to center
    semi_center_cols = [1, 4]  # Columns adjacent to center
    
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == AI:
                # Score center positions highly
                if (row, col) in center_positions:
                    score += center_positions[(row, col)]
                    
                    # Check for connected center pieces
                    for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
                        r, c = row + dr, col + dc
                        if (r, c) in center_positions and board[r][c] == AI:
                            score += 10  # Bonus for connected center pieces
                            
                # Score positions adjacent to center
                elif row in semi_center_rows and col in semi_center_cols:
                    score += 4  # Corner positions near center
                elif row in semi_center_rows or col in semi_center_cols:
                    score += 3  # Edge positions near center
                else:
                    score += 1  # Edge positions
            
            elif board[row][col] == PLAYER:
                # Penalty for opponent controlling center
                if (row, col) in center_positions:
                    score -= 12  # Higher penalty for opponent center control
                    
                    # Extra penalty for connected center pieces
                    for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
                        r, c = row + dr, col + dc
                        if (r, c) in center_positions and board[r][c] == PLAYER:
                            score -= 15  # Severe penalty for opponent's connected center pieces
    
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
def check_center_threat(board):
    """Check for immediate threats in center rows/columns and diagonals"""
    # Check center rows (2-3)
    for row in [2, 3]:
        for col in range(BOARD_SIZE - 1):
            if (board[row][col] == board[row][col+1] == PLAYER and 
                board[row][col] is not None):
                # Check if this pair can be extended
                if col > 0 and board[row][col-1] is None:
                    return (row, col-1)
                if col < BOARD_SIZE-2 and board[row][col+2] is None:
                    return (row, col+2)
    
    # Check center columns (2-3)
    for col in [2, 3]:
        for row in range(BOARD_SIZE - 1):
            if (board[row][col] == board[row+1][col] == PLAYER and 
                board[row][col] is not None):
                # Check if this pair can be extended
                if row > 0 and board[row-1][col] is None:
                    return (row-1, col)
                if row < BOARD_SIZE-2 and board[row+2][col] is None:
                    return (row+2, col)
    
    # Enhanced diagonal threat detection
    def check_diagonal_sequence(board, row, col, direction):
        """Check diagonal sequences in given direction ('main' or 'anti')"""
        count = 0
        empty_before = None
        empty_after = None
        
        if direction == 'main':
            # Check main diagonal (top-left to bottom-right)
            # Check backward
            r, c = row, col
            while r > 0 and c > 0 and count < 3:
                r, c = r-1, c-1
                if board[r][c] == PLAYER:
                    count += 1
                elif board[r][c] is None:
                    empty_before = (r, c)
                    break
                else:
                    break
            
            # Check forward
            r, c = row, col
            while r < BOARD_SIZE-1 and c < BOARD_SIZE-1 and count < 3:
                r, c = r+1, c+1
                if board[r][c] == PLAYER:
                    count += 1
                elif board[r][c] is None:
                    empty_after = (r, c)
                    break
                else:
                    break
        else:
            # Check anti-diagonal (top-right to bottom-left)
            # Check backward
            r, c = row, col
            while r > 0 and c < BOARD_SIZE-1 and count < 3:
                r, c = r-1, c+1
                if board[r][c] == PLAYER:
                    count += 1
                elif board[r][c] is None:
                    empty_before = (r, c)
                    break
                else:
                    break
            
            # Check forward
            r, c = row, col
            while r < BOARD_SIZE-1 and c > 0 and count < 3:
                r, c = r+1, c-1
                if board[r][c] == PLAYER:
                    count += 1
                elif board[r][c] is None:
                    empty_after = (r, c)
                    break
                else:
                    break
        
        return count, empty_before, empty_after

    # Check all potential diagonal threats
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == PLAYER:
                # Check main diagonal
                count, empty_before, empty_after = check_diagonal_sequence(board, row, col, 'main')
                if count >= 2:
                    if empty_before and (row-2 <= 3 and col-2 <= 3):  # Near center priority
                        return empty_before
                    if empty_after and (row+2 <= 3 and col+2 <= 3):   # Near center priority
                        return empty_after
                    if empty_before:
                        return empty_before
                    if empty_after:
                        return empty_after
                
                # Check anti-diagonal
                count, empty_before, empty_after = check_diagonal_sequence(board, row, col, 'anti')
                if count >= 2:
                    if empty_before and (row-2 <= 3 and col+2 >= 2):  # Near center priority
                        return empty_before
                    if empty_after and (row+2 <= 3 and col-2 >= 2):   # Near center priority
                        return empty_after
                    if empty_before:
                        return empty_before
                    if empty_after:
                        return empty_after
    
    return None

def calculate_diagonal_threat(board, row, col, dr, dc):
    """Calculate the threat level of a diagonal sequence"""
    threat_score = 0
    count = 0
    space_before = False
    space_after = False
    
    # Check forward diagonal
    r, c = row, col
    while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
        if board[r][c] == PLAYER:
            count += 1
        elif board[r][c] is None:
            space_after = True
            break
        else:
            break
        r, c = r + dr, c + dc
    
    # Check backward diagonal
    r, c = row - dr, col - dc
    while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
        if board[r][c] == PLAYER:
            count += 1
        elif board[r][c] is None:
            space_before = True
            break
        else:
            break
        r, c = r - dr, c - dc
    
    # Calculate threat score with emphasis on center proximity
    is_near_center = (1 <= row <= 4) and (1 <= col <= 4)
    if count >= 2:
        if space_before and space_after:
            threat_score = 25 if is_near_center else 15
        elif space_before or space_after:
            threat_score = 15 if is_near_center else 10
    
    return threat_score

def is_center_line(row, col, dr, dc):
    """Check if a line goes through the center region"""
    return (dr == 0 and 2 <= col <= 3) or (dc == 0 and 2 <= row <= 3)

def best_move(board):
    best_val = -math.inf
    moves = []
    
    # Define center and strategic positions
    center_positions = [(2, 2), (2, 3), (3, 2), (3, 3)]
    center_adjacent = [(1, 2), (1, 3), (2, 1), (2, 4), (3, 1), (3, 4), (4, 2), (4, 3)]
    
    # First check for center threats
    center_threat = check_center_threat(board)
    if center_threat:
        return center_threat
    
    # First, try to use learned move
    learned_move = ai_learning.get_learned_move(board)
    if learned_move and board[learned_move[0]][learned_move[1]] is None:
        # Verify if learned move is good in current context
        board[learned_move[0]][learned_move[1]] = AI
        eval_score = evaluate(board)
        board[learned_move[0]][learned_move[1]] = None
        if eval_score > 0:
            return learned_move
    
    # Check for immediate winning move
    for (i, j) in available_moves(board):
        board[i][j] = AI
        if check_winner(board) == AI:
            board[i][j] = None
            ai_learning.record_move(board, (i, j))
            return (i, j)
        board[i][j] = None
    
    # Check for immediate blocking move
    for (i, j) in available_moves(board):
        board[i][j] = PLAYER
        if check_winner(board) == PLAYER:
            board[i][j] = None
            ai_learning.record_move(board, (i, j))
            return (i, j)
        board[i][j] = None
        
    # Early game strategy: Prioritize center control
    if len(available_moves(board)) >= BOARD_SIZE * BOARD_SIZE - 4:  # Early game
        # Try to take center positions first
        for (i, j) in center_positions:
            if board[i][j] is None:
                return (i, j)
                
        # If centers are taken, look for strategic adjacent positions
        for (i, j) in center_adjacent:
            if board[i][j] is None:
                # Check if this creates a potential winning line
                board[i][j] = AI
                if evaluate(board) > 5:  # Threshold for good position
                    board[i][j] = None
                    return (i, j)
                board[i][j] = None
    
    # Check for diagonal opportunities and threats
    diagonal_directions = [(1, 1), (1, -1)]
    for (i, j) in available_moves(board):
        board[i][j] = AI
        move_val = minimax(board, 3, False, -math.inf, math.inf)
        
        # Add bonus for diagonal moves near center
        if 1 <= i <= 4 and 1 <= j <= 4:
            for dr, dc in diagonal_directions:
                # Check both directions from this position
                threat_score = calculate_diagonal_threat(i, j, dr, dc)
                if threat_score > 0:
                    move_val += threat_score
        
        board[i][j] = None
        if move_val > best_val:
            best_val = move_val
            moves = [(i, j)]
        elif move_val == best_val:
            moves.append((i, j))
    
    # Return a random move from the best moves
    return random.choice(moves) if moves else None
