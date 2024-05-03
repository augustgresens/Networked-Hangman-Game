# Networked Hangman Game
The purpose of this project was to create a Hangman game where anyone that is participating can guess a word, and the hangman game continues until the correct word is guessed.
## Server
The server accepts connections from clients, and manages the game.  It broadcasts the final state of the game to each client, and restarts automatically.
```py
# Initialization and Start of the Server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 8000))
server_socket.listen()
print("Server started... Waiting for connections.")
```
```py
# Handling Guesses and Updating Game State
def client_thread(conn, addr, game):
    while True:
        guess = conn.recv(1024).decode().strip().lower()
        result, message = game.guess(guess)
        game_state = json.dumps(game.get_game_state())
        conn.sendall(game_state.encode())
```
## Client
The client provides a user interface for players to interact with the Hangman server.  Players enter their name and the server's IP address and are able to play hangman with multiple other people.  The interface automatically updates while playing.
```py
# Connecting to the Server and Sending Guesses
def setup_connection(self):
    self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.client_socket.connect((self.host, self.port))
    self.client_socket.sendall(self.player_name.encode())

# GUI Element for Guess Submission
self.guess_button = tk.Button(self, text="Guess", command=self.send_guess)
self.guess_button.pack()
```
## How to Run
- Start server script
- Run client script
- Enter a name and the server's IP address
## Features
- Server handles multiple connections
- Game updates in real time for all users
- Interactive GUI
## Technologies Used
- Python
- Tkinter for GUI
- TCP Socket Programming
- Threading for multiple users to join