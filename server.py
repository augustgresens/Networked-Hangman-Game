import socket
import threading
import json
import random


def choose_word():
    """Choose a random word for the hangman game."""
    words = [
        "python",
        "hangman",
        "network",
        "server",
        "client",
        "router",
        "packet",
        "firewall",
        "protocol",
        "wireless",
        "gateway",
        "switch",
        "subnet",
        "socket",
        "bandwidth",
    ]

    return random.choice(words)


class HangmanGame:
    """A class representing a hangman game."""

    def __init__(self):
        """Initialize the hangman game."""
        self.reset_game()
        self.clients = []

    def reset_game(self):
        """Reset the game to start a new round."""
        self.word = choose_word()
        self.masked_word = ["_"] * len(self.word)
        self.attempts = 6
        self.guessed_letters = set()
        self.guesses = []

    def guess(self, name, letter):
        """Make a guess in the hangman game."""
        if letter in self.guessed_letters:
            return False, "Already guessed"
        self.guessed_letters.add(letter)
        self.guesses.append(f"{name} guessed '{letter}'")

        if letter in self.word:
            is_complete = True
            for i, char in enumerate(self.word):
                if char == letter:
                    self.masked_word[i] = letter
                if self.masked_word[i] == "_":
                    is_complete = False
            return is_complete, "You win!" if is_complete else "Correct"
        else:
            self.attempts -= 1
            if self.attempts == 0:
                return True, f"You lose! The word was: {self.word}"
            return False, "Incorrect"

    def get_game_state(self):
        """Get the current state of the game."""
        return {
            "masked_word": "".join(self.masked_word),
            "attempts": self.attempts,
            "guessed_letters": list(self.guessed_letters),
            "guesses": self.guesses,
        }

    def broadcast(self, message):
        """Send a message to all connected clients."""
        for client in self.clients[:]:
            try:
                client.sendall(message)
            except socket.error:
                self.clients.remove(client)


def client_thread(conn, addr, game):
    """Handle guesses and update game state for a client."""
    try:
        name = conn.recv(1024).decode()
        if not name:
            raise ValueError("No name received from the client.")
        print(f"{name} has connected from {addr}")
        game.clients.append(conn)

        while True:
            data = conn.recv(1024).decode().lower().strip()
            if not data:
                break
            result, message = game.guess(name, data)
            game_state = game.get_game_state()
            game_state.update({"result": result, "message": message})
            broadcast_data = json.dumps(game_state).encode()
            game.broadcast(broadcast_data)
            if message == "You win!" or message.startswith("You lose"):
                game.reset_game()
    except ConnectionResetError:
        print(f"Connection with {name} has been lost.")
    finally:
        game.clients.remove(conn)
        conn.close()


def main():
    """Start the hangman server."""
    host = "0.0.0.0"
    port = 8000
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()
    game = HangmanGame()
    print("Server started... Waiting for connections.")
    try:
        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=client_thread, args=(conn, addr, game)).start()
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
