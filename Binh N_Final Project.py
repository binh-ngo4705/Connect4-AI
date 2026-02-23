import tkinter as tk
from tkinter import messagebox
import random

class Connect4:
    def __init__(self, width=7, height=6):
        self.width = width
        self.height = height
        self.board = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        
    def __str__(self):
        s = ''
        for row in self.board:
            s += '|' + '|'.join(row) + '|\n'
        s += '--' * self.width + '-\n'
        s += ' '.join(str(i % 10) for i in range(self.width)) + '\n'
        return s

    def is_legal_move(self, col):
        if 0 <= col < self.width:
            return self.board[0][col] == ' '
        return False

    def add_move(self, col, player):
        if not self.is_legal_move(col):
            return -1  # Return -1 for illegal moves
        
        # Find the bottom-most empty row in the column
        for row in range(self.height-1, -1, -1):
            if self.board[row][col] == ' ':
                self.board[row][col] = player
                return row  # Return the row where the piece was placed
        return -1
    
    def del_move(self, col):
        if col < 0 or col >= self.width:
            return
        for row in range(self.height):
            if self.board[row][col] != ' ':
                self.board[row][col] = ' '
                return            
    
    def clear(self):
        for row in range(self.height):
            for col in range(self.width):
                self.board[row][col] = ' '

    def is_full(self):
        for col in range(self.width):
            if self.is_legal_move(col):
                return False
        return True 

    def is_win_for(self, player):
        # Check horizontal wins
        for row in range(self.height):
            for col in range(self.width - 3):
                if (self.board[row][col] == player and 
                    self.board[row][col+1] == player and 
                    self.board[row][col+2] == player and 
                    self.board[row][col+3] == player):
                    return True
        
        # Check vertical wins
        for row in range(self.height - 3):
            for col in range(self.width):
                if (self.board[row][col] == player and 
                    self.board[row+1][col] == player and 
                    self.board[row+2][col] == player and 
                    self.board[row+3][col] == player):
                    return True
        
        # Check diagonal (top-left to bottom-right)
        for row in range(self.height - 3):
            for col in range(self.width - 3):
                if (self.board[row][col] == player and 
                    self.board[row+1][col+1] == player and 
                    self.board[row+2][col+2] == player and 
                    self.board[row+3][col+3] == player):
                    return True
        
        # Check diagonal (bottom-left to top-right)
        for row in range(3, self.height):
            for col in range(self.width - 3):
                if (self.board[row][col] == player and 
                    self.board[row-1][col+1] == player and 
                    self.board[row-2][col+2] == player and 
                    self.board[row-3][col+3] == player):
                    return True
        
        return False

class Player:
    def __init__(self, player, tiebreaker='LEFT', ply=4):
        self.player = player
        self.tiebreaker = tiebreaker
        self.ply = ply
    
    def __str__(self):
        return f'AI Token: {self.player} using {self.tiebreaker} tiebreaking at {self.ply} ply'
    
    def next_move(self, board):
        scores = self._scores_for(board, self.player, self.ply)
        max_score = max(scores)
        best_columns = [col for col, score in enumerate(scores) if score == max_score]
        
        if self.tiebreaker == 'LEFT':
            return best_columns[0]
        elif self.tiebreaker == 'RIGHT':
            return best_columns[-1]
        else:  # RANDOM
            return random.choice(best_columns)
    
    def _scores_for(self, board, player, ply):
        scores = []
    
        for col in range(board.width):
            if not board.is_legal_move(col):
                scores.append(-1)
                continue
        
            board.add_move(col, player)
        
            if board.is_win_for(player):
                scores.append(100)
            else:
                if ply > 1:
                    opponent = 'O' if player == 'X' else 'X'
                    opponent_scores = self._scores_for(board, opponent, ply - 1)
                    best_opponent_score = max(opponent_scores)
                    scores.append(100 - best_opponent_score)
                else:
                    scores.append(50)
        
            board.del_move(col)
    
        return scores

class Connect4GUI:
    def __init__(self, window):
        self.window = window
        self.window.title("Connect 4")
        
        # Game objects
        self.game = Connect4()
        self.ai_player = Player('O', 'RANDOM', 4)
        self.current_player = 'X'  # Human starts
        
        # Colors
        self.colors = {
            ' ': '#1E90FF',  # Blue for empty slots
            'X': '#FFFF00',  # Yellow for human
            'O': '#FF0000',  # Red for AI
            'bg': '#1E90FF', # Blue background
            'grid': '#000080' # Dark blue for grid
        }
        
        # GUI dimensions
        self.cell_size = 80
        self.width = self.game.width * self.cell_size
        self.height = self.game.height * self.cell_size  # Extra row for "next piece" indicator
        
        self.setup_gui()
        self.update_display()
    
    def setup_gui(self):
        # Main frame
        self.main_frame = tk.Frame(self.window)
        self.main_frame.pack(padx=10, pady=10)
        
        # Control frame (buttons and info)
        self.control_frame = tk.Frame(self.main_frame)
        self.control_frame.pack(fill='x', pady=5)
        
        # Quit button
        self.quit_button = tk.Button(self.control_frame, text="Quit", command=self.quit_game, 
                                   bg='red', fg='white', font=('Arial', 12))
        self.quit_button.pack(side='right', padx=5)
        
        # New Game button
        self.new_button = tk.Button(self.control_frame, text="New Game", command=self.new_game,
                                  bg='green', fg='white', font=('Arial', 12))
        self.new_button.pack(side='right', padx=5)
        
        # AI Difficulty slider
        self.difficulty_frame = tk.Frame(self.control_frame)
        self.difficulty_frame.pack(side='left')
        
        tk.Label(self.difficulty_frame, text="AI Difficulty:", font=('Arial', 10)).pack(side='left')
        self.difficulty = tk.Scale(self.difficulty_frame, from_=1, to=6, orient='horizontal',
                                 length=150, command=self.change_difficulty)
        self.difficulty.set(4)  # Default to 4-ply
        self.difficulty.pack(side='left', padx=5)
        
        # Status label
        self.status_label = tk.Label(self.control_frame, text="Your turn! Click a column to play.", 
                                   font=('Arial', 12, 'bold'))
        self.status_label.pack(side='left', padx=10)
        
        # Canvas for game board
        self.canvas = tk.Canvas(self.main_frame, width=self.width, height=self.height, 
                              bg=self.colors['bg'], highlightthickness=0)
        self.canvas.pack(pady=5)
        
        # Bind mouse events
        self.canvas.bind('<Button-1>', self.canvas_click)
        self.canvas.bind('<Motion>', self.mouse_motion)
        
        # Draw the board
        self.draw_board()
    
    def draw_board(self):
        self.canvas.delete("all")
        
        # Draw the grid holes
        for row in range(self.game.height):
            for col in range(self.game.width):
                x1 = col * self.cell_size + 5
                y1 = row * self.cell_size + 5
                x2 = (col + 1) * self.cell_size - 5
                y2 = (row + 1) * self.cell_size - 5
                
                # Draw circle for each slot
                self.canvas.create_oval(x1, y1, x2, y2, fill=self.colors[' '], 
                                      outline=self.colors['grid'], width=2)
    
    def update_display(self):
        # Update the pieces on the board
        for row in range(self.game.height):
            for col in range(self.game.width):
                x1 = col * self.cell_size + 5
                y1 = row * self.cell_size + 5
                x2 = (col + 1) * self.cell_size - 5
                y2 = (row + 1) * self.cell_size - 5
                
                piece = self.game.board[row][col]
                color = self.colors[piece]
                
                # Create or update the piece
                self.canvas.create_oval(x1, y1, x2, y2, fill=color, 
                                      outline=self.colors['grid'], width=2)
    
    def mouse_motion(self, event):
        # Show where the next piece would go
        if self.current_player == 'X' and not self.game_over():
            col = event.x // self.cell_size
            if 0 <= col < self.game.width:
                # Clear the top row
                self.canvas.delete("preview")
                
                # Draw preview piece
                x1 = col * self.cell_size + 5
                y1 = 5
                x2 = (col + 1) * self.cell_size - 5
                y2 = self.cell_size - 5
                
                self.canvas.create_oval(x1, y1, x2, y2, fill=self.colors['X'], 
                                      outline='black', width=2, tags="preview")
    
    def canvas_click(self, event):
        if self.current_player != 'X' or self.game_over():
            return
        
        col = event.x // self.cell_size
        
        if not self.game.is_legal_move(col):
            messagebox.showwarning("Invalid Move", "Column is full or doesn't exist!")
            return
        
        # Human makes move
        self.make_move(col, 'X')
        
        # Check if human won
        if self.game.is_win_for('X'):
            self.status_label.config(text="You win! 🎉")
            messagebox.showinfo("Game Over", "Congratulations! You won!")
            return
        
        # Check for tie
        if self.game.is_full():
            self.status_label.config(text="It's a tie! 🤝")
            messagebox.showinfo("Game Over", "The game is a tie!")
            return
        
        # AI's turn
        self.current_player = 'O'
        self.status_label.config(text="AI is thinking...")
        self.window.update()  # Update display immediately
        
        # Schedule AI move after a short delay
        self.window.after(500, self.ai_move)
    
    def make_move(self, col, player):
        row = self.game.add_move(col, player)
        if row != -1:  # If move was successful
            self.animate_piece(col, row, player)
            self.update_display()
    
    def animate_piece(self, col, row, player):
        # Simple animation: piece drops from top
        start_y = 5
        end_y = row * self.cell_size + 5
        
        x1 = col * self.cell_size + 5
        x2 = (col + 1) * self.cell_size - 5
        
        # Create moving piece
        piece = self.canvas.create_oval(x1, start_y, x2, start_y + self.cell_size - 10, 
                                      fill=self.colors[player], outline='black', width=2)
        
        # Animate dropping
        for y in range(start_y, end_y, 10):
            self.canvas.coords(piece, x1, y, x2, y + self.cell_size - 10)
            self.window.update()
            self.window.after(30)  # Small delay for animation
        
        # Remove the animated piece (real piece is drawn by update_display)
        self.canvas.delete(piece)
    
    def ai_move(self):
        if self.game_over():
            return
            
        # AI makes move
        col = self.ai_player.next_move(self.game)
        self.make_move(col, 'O')
        
        # Check if AI won
        if self.game.is_win_for('O'):
            self.status_label.config(text="AI wins! 🤖")
            messagebox.showinfo("Game Over", "The AI won!")
            return
        
        # Check for tie
        if self.game.is_full():
            self.status_label.config(text="It's a tie! 🤝")
            messagebox.showinfo("Game Over", "The game is a tie!")
            return
        
        # Back to human's turn
        self.current_player = 'X'
        self.status_label.config(text="Your turn! Click a column to play.")
    
    def change_difficulty(self, value):
        new_ply = int(value)
        self.ai_player.ply = new_ply
        self.status_label.config(text=f"AI difficulty set to {new_ply}-ply")
    
    def game_over(self):
        return (self.game.is_win_for('X') or self.game.is_win_for('O') or 
                self.game.is_full())
    
    def new_game(self):
        self.game.clear()
        self.current_player = 'X'
        self.status_label.config(text="Your turn! Click a column to play.")
        self.update_display()
        self.canvas.bind('<Button-1>', self.canvas_click)
    
    def quit_game(self):
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            self.window.destroy()

def main():
    root = tk.Tk()
    app = Connect4GUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()