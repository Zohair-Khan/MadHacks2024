from flask import Flask, jsonify, request, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
import os
from flask_cors import CORS
import requests
from ai_api import fight
from collections import deque

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
CORS(app)

VIEW_GAME_LINK = "http://127.0.0.1:5000/view_game/"

games = []

waiting_queue = deque()

@app.route('/')
def login():
    """Login page for entering username."""
    return render_template('login.html')


@app.route("/new_game_id")
def new_game_id():
    game = {
        "id": len(games),
        "players": [],
        "turns": [],
        "current_turn": 0,
    }
    games.append(game)
    return jsonify(len(games)-1)


# /game_setup/<game_id>?players=["player1","player2"]
@app.route("/game_setup/<game_id>")
def game_setup(game_id):
    game_id = int(game_id)  # Convert game_id to an integer
    players = eval(request.args.get('players'))
    games[game_id]["players"] += players
    games[game_id]["turn_player"] = players[0]
    return jsonify(games)

@app.route("/play_turn/<game_id>")
def play_turn(game_id):
    game_id = int(game_id)  # Convert game_id to an integer
    player = request.args.get('player')
    champion = request.args.get('champion')
    if(player == games[game_id]["turn_player"] and len(champion) != 0):
        if(games[game_id]["current_turn"] == 0):
            turn_result = {
                "turnplayer": games[game_id]["turn_player"],
                "champion": champion,
                "prev_champion": champion,
                "champion_wins": True,
                "how_champion_wins": f"{games[game_id]['turn_player']} has chosen a champion!"
            }
            # Change turnplayer to the other player
            games[game_id]["turn_player"] = games[game_id]["players"][0] if games[game_id]["players"][0] != player else games[game_id]["players"][1]
            
            games[game_id]["current_turn"] = games[game_id]["current_turn"] + 1
            
            

        elif(games[game_id]["current_turn"] > 0):
            current_turn = games[game_id]["current_turn"]
            prev_champion = games[game_id]["turns"][current_turn-1]["champion"]
            print(f"CURRENTTURN CURRENTTURN {current_turn}")

            fightresults = fight(champion, prev_champion)


            turn_result = {
                "turnplayer": games[game_id]["turn_player"],
                "champion": champion,
                "prev_champion": prev_champion,
                "how_champion_wins": fightresults["how_champion_wins"]
            }

            turn_result['champion_wins'] = (champion == fightresults['champion'])

            print(turn_result['champion_wins'])

            if(turn_result['champion_wins']):
                # Change turnplayer to the other player
                games[game_id]["turn_player"] = games[game_id]["players"][0] if games[game_id]["players"][0] != player else games[game_id]["players"][1]
                
                games[game_id]["current_turn"] = games[game_id]["current_turn"] + 1
        
            else:
                games[game_id]["winner"] = games[game_id]["players"][0] if games[game_id]["players"][0] != player else games[game_id]["players"][1]

        games[game_id]["turns"].append(turn_result)
        
        

    return jsonify(games[game_id])

@app.route("/view_game/<game_id>")
def view_game(game_id):
    game_id = int(game_id)
    return jsonify(games[game_id])


if __name__ == "__main__":
    app.run(debug=True)