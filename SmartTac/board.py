# board.py
import tkinter as tk
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BOARD_SIZE, CELL_SIZE,
    WHITE, BLACK, RED, BLUE, GREEN,
    PLAYER, AI, FONT_NAME, FONT_SIZE
)
from ai_engine import check_winner, available_moves, best_move
import time

class Board:
    def __init__(self, root):
        self.root = root
        
        # Create main frame to hold all widgets
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Create game area frame
        self.game_area = tk.Frame(self.main_frame)
        self.game_area.pack(expand=True, fill='both')
        
        # Create canvas for the game board
        self.canvas = tk.Canvas(
            self.game_area,
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
            bg=WHITE
        )
        self.canvas.pack(expand=True)
        
        # Initialize game state
        self.grid = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.canvas.bind("<Button-1>", self.handle_click)
        self.game_over = False
        self.winner_cells = []
        
        # Create top control panel frame for New Game button
        self.top_control_panel = tk.Frame(self.main_frame)
        self.top_control_panel.pack(fill='x', pady=(0, 10))
        
        # Reset button with improved style - now at the top
        self.reset_button = tk.Button(
            self.top_control_panel,
            text="New Game",
            command=self.reset_game,
            font=(FONT_NAME, 14, 'bold'),  # Made font bigger and bold
            relief=tk.RAISED,
            bd=3,
            padx=30,
            pady=8,
            bg='#4CAF50',  # Green background
            fg='white',    # White text
            cursor='hand2' # Hand cursor on hover
        )
        self.reset_button.pack(pady=5)
        
        # Create bottom control panel frame
        self.control_panel = tk.Frame(self.main_frame)
        self.control_panel.pack(fill='x', pady=10)
        
        # Status label
        self.status_label = tk.Label(
            self.control_panel,
            text="Your turn (X)",
            font=(FONT_NAME, 16)
        )
        self.status_label.pack()
        
        # Score frame
        self.score_frame = tk.Frame(self.control_panel)
        self.score_frame.pack(pady=5)
        
        # Initialize scores
        self.player_score = 0
        self.ai_score = 0
        
        # Player score label
        self.player_score_label = tk.Label(
            self.score_frame,
            text=f"You: {self.player_score}",
            font=(FONT_NAME, 14)
        )
        self.player_score_label.pack(side=tk.LEFT, padx=20)
        
        # AI score label
        self.ai_score_label = tk.Label(
            self.score_frame,
            text=f"AI: {self.ai_score}",
            font=(FONT_NAME, 14)
        )
        self.ai_score_label.pack(side=tk.LEFT, padx=20)
        
        self.current_player = PLAYER
        self.draw_board()

    def draw_board(self):
        """Draw the game board"""
        self.canvas.delete("all")
        
        # Draw grid lines
        for i in range(1, BOARD_SIZE):
            # Vertical lines
            self.canvas.create_line(
                i * CELL_SIZE, 0,
                i * CELL_SIZE, SCREEN_HEIGHT,
                fill=BLACK
            )
            # Horizontal lines
            self.canvas.create_line(
                0, i * CELL_SIZE,
                SCREEN_WIDTH, i * CELL_SIZE,
                fill=BLACK
            )
        
        # Draw marks
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                mark = self.grid[row][col]
                if mark:
                    x = col * CELL_SIZE + CELL_SIZE//2
                    y = row * CELL_SIZE + CELL_SIZE//2
                    color = RED if mark == PLAYER else BLUE
                    if check_winner(self.grid) and mark == check_winner(self.grid):
                        color = GREEN
                    self.canvas.create_text(x, y, text=mark, fill=color,
                                         font=(FONT_NAME, FONT_SIZE))

    def handle_click(self, event):
        """Handle mouse click events"""
        if self.game_over or self.current_player != PLAYER:
            return
            
        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE
        
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            if self.grid[row][col] is None:
                # Player's move
                self.grid[row][col] = PLAYER
                self.draw_board()
                
                if self.check_game_end():
                    return
                    
                # AI's turn
                self.current_player = AI
                self.status_label.config(text="AI is thinking...")
                self.root.update()
                
                # Add a small delay to make AI's move visible
                self.root.after(500, self.ai_move)

    def ai_move(self):
        """Handle AI's move"""
        move = best_move(self.grid)
        if move:
            row, col = move
            self.grid[row][col] = AI
            self.draw_board()
            
            if not self.check_game_end():
                self.current_player = PLAYER
                self.status_label.config(text="Your turn (X)")

    def check_game_end(self):
        """Check if the game has ended"""
        winner = check_winner(self.grid)
        if winner:
            self.game_over = True
            if winner == PLAYER:
                self.player_score += 1
                self.status_label.config(text="You win!")
            else:
                self.ai_score += 1
                self.status_label.config(text="AI wins!")
            self.update_score_labels()
            return True
            
        if not available_moves(self.grid):
            self.game_over = True
            self.status_label.config(text="It's a tie!")
            return True
            
        return False

    def update_score_labels(self):
        """Update the score display"""
        self.player_score_label.config(text=f"You: {self.player_score}")
        self.ai_score_label.config(text=f"AI: {self.ai_score}")

    def reset_game(self):
        """Reset the game state"""
        self.grid = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = PLAYER
        self.game_over = False
        self.winner_cells = []
        self.status_label.config(text="Your turn (X)")
        self.draw_board()