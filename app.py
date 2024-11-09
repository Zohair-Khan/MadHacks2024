from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
from ai_api import generate_text
from db import init_db, get_db
from models import Game

import os

# Load environment variables
load_dotenv()

# Initialize Flask and SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
socketio = SocketIO(app)

# Initialize the database
init_db()

@app.route('/')
def index():
    return render_template('index.html')

# Event for handling game moves
@socketio.on('submit_move')
def handle_submit_move(data):
    prompt = data.get("prompt")
    if not prompt:
        emit('error', {'message': 'Prompt is required.'})
        return

    # Call the AI API to generate a response
    response = generate_text(prompt)

    # Check the response and send it back to the client
    if response:
        emit('move_result', {'result': response})
    else:
        emit('error', {'message': 'Failed to generate a response from the AI API.'})

# Run the app
if __name__ == '__main__':
    socketio.run(app, debug=True)
