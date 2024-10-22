import sqlite3
from dotenv import load_dotenv
import os
from flask import Flask, render_template, request, url_for, flash, redirect

def get_db_connection():
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    return con

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

@app.route('/')
def index():
    con = get_db_connection()
    players = con.execute('SELECT * FROM players ORDER BY elo DESC').fetchall()
    con.close()
    return render_template('index.html', players=players)

@app.route('/input', methods=('GET', 'POST'))
def input():
    if request.method == 'POST':
        name = request.form['name']
        elo = request.form['elo']

        if not name:
            flash("Name is required!")
        # check if name is already taken
        else:
            if not elo: elo = 100
            con = get_db_connection()
            con.execute('INSERT INTO players VALUES (?, ?)', (name, elo))
            con.commit()
            con.close()
            return redirect(url_for('index'))

    return render_template('input.html')