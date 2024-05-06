import socket
import json
import tkinter as tk
from tkinter import messagebox
import threading


class HangmanClient(tk.Frame):
    """Tkinter GUI for a Hangman game client."""

    def __init__(self, master=None):
        """Initialize the client and set up the UI."""
        super().__init__(master)
        self.master = master
        self.canvas = None
        self.word_label = None
        self.guess_entry = None
        self.guess_button = None
        self.status_label = None
        self.guesses_label = None
        self.win_loss_tally = {
            "wins": 0,
            "losses": 0,
        }
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        """Create the initial set of widgets for the game."""
        self.name_label = tk.Label(self, text="Enter your name:")
        self.name_label.pack()

        self.name_entry = tk.Entry(self)
        self.name_entry.pack()

        self.ip_label = tk.Label(self, text="Server IP:")
        self.ip_label.pack()

        self.ip_entry = tk.Entry(self)
        self.ip_entry.pack()

        self.connect_button = tk.Button(
            self, text="Connect", command=self.setup_connection
        )
        self.connect_button.pack()

        self.tally_label = tk.Label(
            self,
            text=f"Wins/Losses: {self.win_loss_tally['wins']}/{self.win_loss_tally['losses']}",
        )
        self.tally_label.pack()

    def setup_connection(self):
        """Set up the connection to the server."""
        self.player_name = self.name_entry.get()
        self.host = self.ip_entry.get()
        self.port = 8000
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        self.client_socket.sendall(self.player_name.encode())
        self.initialize_game_ui()
        threading.Thread(target=self.listen_for_updates, daemon=True).start()

    def initialize_game_ui(self):
        """Initialize the game UI after connecting to the server."""
        self.reset_game_ui()

    def reset_game_ui(self):
        """Reset the UI to the initial state."""
        if self.canvas:
            self.canvas.destroy()
        if self.word_label:
            self.word_label.destroy()
        if self.guess_entry:
            self.guess_entry.destroy()
        if self.guess_button:
            self.guess_button.destroy()
        if self.status_label:
            self.status_label.destroy()
        if self.guesses_label:
            self.guesses_label.destroy()

        self.canvas = tk.Canvas(self, width=200, height=250, bg="white")
        self.canvas.pack()
        self.draw_gallows()

        self.word_label = tk.Label(
            self, text="Word: _ _ _ _ _ _", font=("Helvetica", 16)
        )
        self.word_label.pack()
        self.guess_entry = tk.Entry(self)
        self.guess_entry.pack()
        self.guess_button = tk.Button(self, text="Guess", command=self.send_guess)
        self.guess_button.pack()
        self.status_label = tk.Label(self, text="Enter a letter to guess!")
        self.status_label.pack()
        self.guesses_label = tk.Label(self, text="")
        self.guesses_label.pack()

    def draw_gallows(self):
        """Draw the gallows for the hangman."""
        self.canvas.create_line(150, 20, 150, 50)
        self.canvas.create_line(120, 20, 150, 20)
        self.canvas.create_line(120, 20, 120, 200)

    def draw_hangman(self, attempts_left):
        """Draw the hangman based on the remaining attempts."""
        steps = 6 - attempts_left
        self.canvas.delete("hangman")
        if steps > 0:
            self.canvas.create_oval(140, 50, 160, 70, tags="hangman")
        if steps > 1:
            self.canvas.create_line(150, 70, 150, 120, tags="hangman")
        if steps > 2:
            self.canvas.create_line(150, 80, 170, 100, tags="hangman")
        if steps > 3:
            self.canvas.create_line(150, 80, 130, 100, tags="hangman")
        if steps > 4:
            self.canvas.create_line(150, 120, 170, 140, tags="hangman")
        if steps > 5:
            self.canvas.create_line(150, 120, 130, 140, tags="hangman")

    def send_guess(self):
        """Send a guess to the server."""
        guess = self.guess_entry.get().strip().lower()
        if len(guess) == 1 and guess.isalpha():
            self.client_socket.sendall(guess.encode())
        else:
            messagebox.showerror(
                "Invalid Input", "Please enter exactly one letter, silly goose."
            )
        self.guess_entry.delete(0, tk.END)

    def update_display(self, game_state):
        """Update the display based on the current game state."""
        self.word_label.config(text="Word: " + " ".join(game_state["masked_word"]))
        self.status_label.config(
            text=f"Attempts Left: {game_state['attempts']}, Guessed: {', '.join(game_state['guessed_letters'])}"
        )
        self.guesses_label.config(text="\n".join(game_state["guesses"]))
        self.draw_hangman(game_state["attempts"])

        if "You win!" in game_state["message"]:
            self.win_loss_tally["wins"] += 1
            messagebox.showinfo("Game Over", game_state["message"])
            self.reset_game_ui()
        elif "You lose" in game_state["message"]:
            self.win_loss_tally["losses"] += 1
            messagebox.showinfo("Game Over", game_state["message"])
            self.reset_game_ui()

        self.tally_label.config(
            text=f"Wins/Losses: {self.win_loss_tally['wins']}/{self.win_loss_tally['losses']}"
        )

    def listen_for_updates(self):
        """Listen for updates from the server."""
        while True:
            try:
                response = self.client_socket.recv(1024).decode()
                if response:
                    game_state = json.loads(response)
                    self.update_display(game_state)
                else:
                    break
            except Exception as e:
                print("Error:", e)
                break


def main():
    """Start the Hangman client."""
    root = tk.Tk()
    root.state("zoomed")
    app = HangmanClient(master=root)
    app.mainloop()


if __name__ == "__main__":
    main()
