import json
import os
from typing import List, Dict, Tuple
import random

class AILearning:
    def __init__(self):
        self.memory_file = "ai_memory.json"
        self.board_states = self.load_memory()
        self.current_game_moves = []
        
    def load_memory(self) -> Dict:
        """Load previous learning data"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_memory(self):
        """Save learning data to file"""
        with open(self.memory_file, 'w') as f:
            json.dump(self.board_states, f)
    
    def board_to_key(self, board: List[List[str]]) -> str:
        """Convert board state to string key"""
        return ''.join(''.join(cell if cell is not None else '_' for cell in row) for row in board)
    
    def record_move(self, board: List[List[str]], move: Tuple[int, int]):
        """Record a move for the current game"""
        # Create a deep copy of the board before the move
        board_state = [[cell for cell in row] for row in board]
        board_key = self.board_to_key(board_state)
        self.current_game_moves.append((board_key, move))
    
    def learn_from_game(self, won: bool):
        """Update learning based on game outcome"""
        reward = 1 if won else -1
        
        for board_key, move in self.current_game_moves:
            if board_key not in self.board_states:
                self.board_states[board_key] = {}
            
            move_key = f"{move[0]},{move[1]}"
            if move_key not in self.board_states[board_key]:
                self.board_states[board_key][move_key] = {"wins": 0, "plays": 0}
            
            self.board_states[board_key][move_key]["plays"] += 1
            self.board_states[board_key][move_key]["wins"] += (1 if won else 0)
        
        self.current_game_moves = []  # Reset for next game
        self.save_memory()
    
    def get_learned_move(self, board: List[List[str]]) -> Tuple[int, int]:
        """Get move based on learning history"""
        try:
            board_key = self.board_to_key(board)
            
            if board_key in self.board_states:
                moves = self.board_states[board_key]
                best_ratio = -1
                best_moves = []
                
                for move_key, stats in moves.items():
                    try:
                        if stats["plays"] > 0:
                            ratio = stats["wins"] / stats["plays"]
                            row, col = map(int, move_key.split(','))
                            
                            # Verify move is still valid
                            if 0 <= row < len(board) and 0 <= col < len(board[0]) and board[row][col] is None:
                                if ratio > best_ratio:
                                    best_ratio = ratio
                                    best_moves = [(row, col)]
                                elif ratio == best_ratio:
                                    best_moves.append((row, col))
                    except (ValueError, IndexError):
                        continue
                
                if best_moves and best_ratio > 0.4:  # Only use learned moves if they have decent success
                    return random.choice(best_moves)
            
            return None  # No good learned move available
        except Exception as e:
            print(f"Error in get_learned_move: {e}")
            return None