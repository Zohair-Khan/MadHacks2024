from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit, join_room
from dotenv import load_dotenv
import os
import queue

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
socketio = SocketIO(app, manage_session=True)

# Queue and game tracking
client_queue = queue.Queue()
games_in_progress = {}
username_sid_map = {}  # Track mapping of username to session IDs (sids)

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

@socketio.on('connect')
def handle_connect():
    """Handles client connection and stores their sid."""
    username = session.get('username')
    if username:
        username_sid_map[username] = request.sid
        print(f"[DEBUG] {username} connected with sid {request.sid}.")

@socketio.on('join_queue')
def join_queue():
    """Handles adding user to the queue and pairing."""
    username = session.get('username')
    if username:
        print(f"[DEBUG] {username} has joined the queue.")
        # Attempt to pair clients immediately
        pair_clients()

def pair_clients():
    """Pair two clients if available and start a game."""
    if client_queue.qsize() >= 2:
        player1 = client_queue.get()
        player2 = client_queue.get()

        # Create a unique game ID and initialize the game
        game_id = f"game_{player1}_{player2}"
        games_in_progress[game_id] = {
            "players": [player1, player2],
            "current_turn": player1,  # Set player1 as the starting player
            "moves": []
        }

        # Retrieve sids using username-to-sid mapping
        player1_sid = username_sid_map.get(player1)
        player2_sid = username_sid_map.get(player2)

        print(f"[DEBUG] Pairing {player1} and {player2} with game_id {game_id}.")
        
        if player1_sid and player2_sid:
            # Correct order: sid first, then the room name (game_id)
            join_room(player1_sid, game_id)
            join_room(player2_sid, game_id)
            print(f"[DEBUG] {player1} and {player2} have joined room {game_id}")

            # Notify both players to redirect to the game page
            socketio.emit('start_game', {'game_id': game_id, 'opponent': player2, 'is_turn': True}, to=player1_sid)
            socketio.emit('start_game', {'game_id': game_id, 'opponent': player1, 'is_turn': False}, to=player2_sid)

            # Immediately notify Player 1 to start their turn
            print(f"[DEBUG] Emitting start_turn to {player1}")
            socketio.emit('start_turn', {'player': player1}, to=player1_sid)

            # Notify Player 2 that they should wait for their turn
            print(f"[DEBUG] Emitting waiting_turn to {player2}")
            socketio.emit('waiting_turn', {'player': player1}, to=player2_sid)
        else:
            print(f"[ERROR] Could not retrieve sids for {player1} or {player2}.")

@app.route('/game/<game_id>')
def game(game_id):
    """Dynamic game page."""
    return render_template('game.html', game_id=game_id)

@socketio.on('submit_move')
def handle_submit_move(data):
    """Handles move submissions and turn-switching."""
    game_id = data.get("game_id")
    prompt = data.get("prompt")
    game = games_in_progress.get(game_id)
    username = session.get('username')

    if game and game['current_turn'] == username:
        # Generate AI response and switch turn
        response = generate_text(prompt)
        game['moves'].append({"player": username, "prompt": prompt, "response": response})
        game['current_turn'] = game['players'][1] if game['current_turn'] == game['players'][0] else game['players'][0]

        # Notify both players of the move and turn change
        socketio.emit('move_result', {'prompt': prompt, 'response': response, 'player': username}, room=game_id)
        
        # Notify the next player to take their turn
        next_player = game['current_turn']
        next_player_sid = username_sid_map.get(next_player)
        socketio.emit('start_turn', {'player': next_player}, room=next_player_sid)
    else:
        emit('error', {'message': 'Not your turn.'})

if __name__ == '__main__':
    socketio.run(app, debug=True)
