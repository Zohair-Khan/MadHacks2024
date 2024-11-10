import sqlite3
from flask import g

DATABASE = 'game.db'

# Retreive the items from the database
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# Initialize the database with categories and save it
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS games (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          player TEXT NOT NULL,
                          score INTEGER,
                          time_taken REAL)''')
        conn.commit()

# To close the database connection after each request
def close_db(e=None):
    db = g.pop('_database', None)
    if db is not None:
        db.close()