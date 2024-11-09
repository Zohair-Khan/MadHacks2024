# MadHacks2024
We were watching Dragon Ball on the monitor we rented from MLH while making this
sleep :( is for the week 😈


setup 

# Activate Environment
.\env\Scripts\Activate #activate the environment in windows powershell

source env/bin/activate  # Activate the environment in linux

# install required packages
pip install flask flask-socketio google-cloud-aiplatform python-dotenv

This MADHACKS project is composed of a server, database, and API calls to gemini for dynamic querying.

The server continously runs and accepts new joining clients to a priority queue. It will add them in order and pair up the top two
users to play against each other. The first user will submit a english word or phrase for the other player to respond to. The other
user must submit a word or phrase greater in power than what the first user submitted to win. If the second user fails to defeat the
first user's input, the game is over in two turns. Otherwise, the game continues until a user fails to submit a successful response
to their opponent.