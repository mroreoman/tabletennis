import sqlite3
from dotenv import load_dotenv
import os
from flask import Flask, render_template, request, url_for, flash, redirect
from datetime import date

def get_db_connection():
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    return con

def get_names():
    con = get_db_connection()
    names = [row['name'] for row in con.execute('SELECT name FROM players').fetchall()]
    con.close()
    return names

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

@app.route('/')
def index():
    return redirect('/rankings')

@app.route('/rankings')
def rankings():
    con = get_db_connection()
    players = con.execute('SELECT * FROM players ORDER BY elo DESC').fetchall()
    con.close()
    return render_template('rankings.html', players=players)


@app.route('/player', methods=('GET', 'POST'))
def player():
    if request.method == 'POST':
        name = request.form['name']
        elo = request.form['elo']

        if not name:
            flash("Name is required!")
        elif not name in get_names():
            flash("Name is taken!")
        else:
            if not elo: elo = 100
            con = get_db_connection()
            con.execute('INSERT INTO players VALUES (?, ?)', (name, elo))
            con.commit()
            con.close()
            return redirect(url_for('index'))

    return render_template('player.html')

@app.route('/match', methods=('GET', 'POST'))
def match():
    if request.method == 'POST':
        player1 = request.form['player1']
        score1 = request.form['score1']
        player2 = request.form['player2']
        score2 = request.form['score2']
        d = date.today()

        print(d,player1,score1,player2,score2)
    
    return render_template('match.html', names=get_names())