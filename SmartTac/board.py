# board.py
import tkinter as tk
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BOARD_SIZE, CELL_SIZE,
    WHITE, BLACK, RED, BLUE, GREEN,
    PLAYER, AI, FONT_NAME, FONT_SIZE
)
from ai_engine import check_winner, available_moves, best_move, ai_learning
import time

class Board:
    def __init__(self, root):
        self.root = root
        
        # Create main frame to hold all widgets
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        def on_resize(event=None):
            # Update the canvas size while maintaining the aspect ratio
            frame_width = self.main_frame.winfo_width() - 40  # Account for padding
            frame_height = self.main_frame.winfo_height() - 140  # Account for controls
            
            # Maintain square aspect ratio
            size = min(frame_width, frame_height)
            if size >= SCREEN_WIDTH:  # Don't scale up beyond original size
                size = SCREEN_WIDTH
                
            if hasattr(self, 'canvas'):
                self.canvas.config(width=size, height=size)
                self.draw_board()  # Redraw the board
                
        # Bind resize event
        self.root.bind('<Configure>', on_resize)
        
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
        # Ignore clicks if game is over or it's not player's turn
        if self.game_over or self.current_player != PLAYER:
            return
            
        # Convert click coordinates to grid position
        try:
            col = event.x // CELL_SIZE
            row = event.y // CELL_SIZE
        except (AttributeError, TypeError):
            return  # Invalid click event
        
        # Validate click position and cell availability
        if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
            return  # Click outside grid
        if self.grid[row][col] is not None:
            return  # Cell already occupied
            
        # Make player's move
        self.grid[row][col] = PLAYER
        self.draw_board()
        
        # Check if game ended after player's move
        if self.check_game_end():
            return
            
        # Prepare for AI's turn
        self.current_player = AI
        self.status_label.config(text="AI is thinking...")
        self.root.update()
        
        # Schedule AI's move with a delay
        self.root.after(500, self._safe_ai_move)
    
    def _safe_ai_move(self):
        """Protected method to safely execute AI's move"""
        try:
            if self.game_over or self.current_player != AI:
                return
            self.ai_move()
        except Exception as e:
            print(f"Error during AI move: {e}")
            self.current_player = PLAYER
            self.status_label.config(text="Your turn (X)")

    def ai_move(self):
        """Handle AI's move"""
        if self.game_over or self.current_player != AI:
            return
            
        move = best_move(self.grid)
        if not move:  # No valid moves available
            self.check_game_end()  # Will handle tie game
            return
            
        row, col = move
        # Validate move before applying
        if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
            print(f"Invalid AI move: ({row}, {col})")
            return
        if self.grid[row][col] is not None:
            print(f"AI attempted to move to occupied cell: ({row}, {col})")
            return
            
        # Make AI's move
        self.grid[row][col] = AI
        self.draw_board()
        
        # Check game end and update state
        if not self.check_game_end():
            self.current_player = PLAYER
            self.status_label.config(text="Your turn (X)")

    def check_game_end(self):
        """Check if the game has ended"""
        try:
            # Check for winner
            winner = check_winner(self.grid)
            if winner:
                self.game_over = True
                if winner == PLAYER:
                    self.player_score += 1
                    self.status_label.config(text="You win!")
                    # AI learns from loss
                    ai_learning.learn_from_game(False)
                else:
                    self.ai_score += 1
                    self.status_label.config(text="AI wins!")
                    # AI learns from win
                    ai_learning.learn_from_game(True)
                self.update_score_labels()
                return True
                
            # Check for tie
            if not available_moves(self.grid):
                self.game_over = True
                self.status_label.config(text="It's a tie!")
                # AI learns from tie (consider it a partial success)
                ai_learning.learn_from_game(True)
                return True
                
            return False
        except Exception as e:
            print(f"Error checking game end: {e}")
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
