from db import get_db

class Game:
    def __init__(self, player, score, time_taken):
        self.player = player
        self.score = score
        self.time_taken = time_taken

    def save(self):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''INSERT INTO games (player, score, time_taken)
                          VALUES (?, ?, ?)''', (self.player, self.score, self.time_taken))
        db.commit()

    @staticmethod
    def get_all():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM games ORDER BY score, time_taken')
        games = cursor.fetchall()
        return games

    @staticmethod
    def get_leaderboard():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT player, score, time_taken FROM games ORDER BY score, time_taken LIMIT 10')
        return cursor.fetchall()