import tkinter as tk
from board import Board
from constants import *

def main():
    # Initialize the root window
    root = tk.Tk()
    root.title("6x6 Tic Tac Toe with AI")
    
    # Set window size and properties
    root.minsize(SCREEN_WIDTH, SCREEN_HEIGHT + 100)  # Extra height for controls
    root.resizable(False, False)
    
    # Configure window position (center on screen)
    window_width = SCREEN_WIDTH
    window_height = SCREEN_HEIGHT + 100
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    
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