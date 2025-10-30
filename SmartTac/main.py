import tkinter as tk
from board import Board
from constants import *

def main():
    # Initialize the root window
    root = tk.Tk()
    root.title("6x6 Tic Tac Toe with AI")
    
    # Set minimum window size
    root.minsize(SCREEN_WIDTH + 40, SCREEN_HEIGHT + 140)  # Extra space for controls and borders
    root.resizable(True, True)  # Allow resizing
    
    # Configure window position (center on screen)
    window_width = SCREEN_WIDTH + 40
    window_height = SCREEN_HEIGHT + 140
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    
    # Add window state handler
    def handle_resize(event):
        # Maintain minimum size
        if event.width < SCREEN_WIDTH + 40:
            root.geometry(f"{SCREEN_WIDTH + 40}x{event.height}")
        if event.height < SCREEN_HEIGHT + 140:
            root.geometry(f"{event.width}x{SCREEN_HEIGHT + 140}")
    
    root.bind("<Configure>", handle_resize)
    
    # Create and start the game
    board = Board(root)
    
    # Start the game loop
    root.mainloop()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise
