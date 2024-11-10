from flask import Flask, render_template, session, request, redirect, url_for, jsonify
from dotenv import load_dotenv
import os
import queue
import requests  # For HTTP requests to gameplay_api
import threading
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')

# Queue and game tracking
client_queue = queue.Queue()  # Queue to hold players waiting for a game
username_game_map = {}  # Map usernames to game IDs

# URL of the gameplay API service (assumes gameplay_api.py is running on port 5001)
GAMEPLAY_API_URL = "http://127.0.0.1:5001/gameplay"

@app.route('/')
def login():
    """Login page for entering username."""
    return render_template('login.html')

@app.route('/join', methods=['POST'])
def join():
    """Handle joining the queue with a username."""
    username = request.form.get('username')
    if username:
        session['username'] = username
        client_queue.put(username)
        print(f"[DEBUG] {username} added to queue.")
        return redirect(url_for('waiting'))
    return redirect(url_for('login'))

@app.route('/waiting')
def waiting():
    """Waiting page where users wait for an opponent."""
    return render_template('waiting.html')

@app.route('/game/<game_id>')
def game(game_id):
    """Dynamic game page."""
    return render_template('game.html', game_id=game_id)

@app.route('/join_queue', methods=['GET'])
def join_queue_route():
    """API endpoint to add the user to the queue."""
    username = session.get('username')
    if username:
        client_queue.put(username)
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route('/check_for_game', methods=['GET'])
def check_for_game():
    """Polls to check if a game has been assigned to the user."""
    username = session.get('username')
    game_id = username_game_map.get(username)
    if game_id is not None:
        return jsonify({"game_id": game_id})
    return jsonify({"game_id": None})

@app.route('/poll_game_state/<game_id>', methods=['GET'])
def poll_game_state(game_id):
    """Endpoint for polling the current state of a game."""
    response = requests.get(f"{GAMEPLAY_API_URL}/get_game_state/{game_id}")
    return jsonify(response.json())

@app.route('/poll_turn/<game_id>', methods=['GET'])
def poll_turn(game_id):
    """Check if it is the player's turn."""
    username = session.get('username')
    if not username:
        return jsonify({"error": "User not logged in"}), 403

    response = requests.get(f"{GAMEPLAY_API_URL}/check_turn/{game_id}", params={"player": username})
    return jsonify(response.json())

@app.route('/submit_move', methods=['POST'])
def submit_move():
    """Handles move submissions."""
    game_id = request.json.get("game_id")
    prompt = request.json.get("prompt")
    username = session.get('username')

    response = requests.post(f"{GAMEPLAY_API_URL}/play_turn/{game_id}", json={"player": username, "champion": prompt})
    return jsonify(response.json())

def pair_clients():
    """Continuously checks the client queue and pairs two clients to start a game."""
    while True:
        # Only proceed if there are at least two players in the queue
        if client_queue.qsize() >= 2:
            # Retrieve two players from the queue
            player1 = client_queue.get()
            player2 = client_queue.get()

            # Request a new game ID from the gameplay_api service
            response = requests.get(f"{GAMEPLAY_API_URL}/new_game_id")
            game_id = response.json().get("game_id")  # Get the game ID from the response

            if game_id is not None:
                # Set up the game with players via gameplay_api service
                requests.get(f"{GAMEPLAY_API_URL}/game_setup/{game_id}", params={'players': [player1, player2]})

                # Map each player to the game ID
                username_game_map[player1] = game_id
                username_game_map[player2] = game_id

                print(f"[DEBUG] Paired {player1} and {player2} in game {game_id}")
            else:
                print("[ERROR] Failed to retrieve a game ID from gameplay_api.")
        
        # Poll the queue every second
        time.sleep(1)

# Start pairing clients in a background thread
threading.Thread(target=pair_clients, daemon=True).start()

if __name__ == '__main__':
    app.run(debug=True)