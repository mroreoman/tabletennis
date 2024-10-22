import sqlite3
from flask import Flask, render_template

def get_db_connection():
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    return con

app = Flask(__name__)

@app.route('/')
def index():
    con = get_db_connection()
    players = con.execute('SELECT * FROM players ORDER BY elo DESC').fetchall()
    con.close()
    return render_template('index.html', players=players)