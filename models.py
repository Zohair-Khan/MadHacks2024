from db import get_db

class Game:
    
    # Assign internal values upon creation
    def __init__(self, player, score, time_taken):
        self.player = player
        self.score = score
        self.time_taken = time_taken

    # Assign all current values to the database and save them
    def save(self):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''INSERT INTO games (player, score, time_taken)
                          VALUES (?, ?, ?)''', (self.player, self.score, self.time_taken))
        db.commit()

    # Retrieve all the data from the database and return the games by score and time taken
    @staticmethod
    def get_all():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM games ORDER BY score, time_taken')
        games = cursor.fetchall()
        return games

    # Retrieve data from the database for the top 10 players by score and time taken
    @staticmethod
    def get_leaderboard():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT player, score, time_taken FROM games ORDER BY score, time_taken LIMIT 10')
        return cursor.fetchall()