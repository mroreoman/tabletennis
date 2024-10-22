import sqlite3
import math
from dotenv import load_dotenv
import os
from flask import Flask, render_template, request, url_for, flash, redirect
from datetime import date

elo_K = 30

def get_db_connection():
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    return con

def get_names():
    con = get_db_connection()
    names = [row['name'] for row in con.execute('SELECT name FROM players').fetchall()]
    con.close()
    return names

def calculate_elo(s1, s2, elo1, elo2):
    odds = 1.0 / (1 + math.pow(10, (elo1 - elo2) / 400.0)) #1=p1 wins, 0=p2 wins

    # sWin = max(s1,s2)
    outcome = ((s1-s2) / max(s1,s2) + 1) / 2 #1=p1 wins, 0=p2 wins
    print(f"odds: {odds}")
    print(f"score: {s1} - {s2}")
    print(f"outcome: {outcome}")

    new1 = elo1 + elo_K * (outcome - odds)
    new2 = elo2 + elo_K * (odds - outcome)
    print(f"p1: {elo1} -> {new1}")
    print(f"p2: {elo2} -> {new2}")

    return (new1, new2)

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
    matches = con.execute('SELECT * FROM matches ORDER BY id DESC').fetchall()
    con.close()
    return render_template('rankings.html', players=players, matches=matches)


@app.route('/player', methods=('GET', 'POST'))
def player():
    if request.method == 'POST':
        name = request.form['name']
        elo = request.form['elo']

        if name in get_names():
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
        print(request.form)
        if not request.form['player1'] or not request.form['player2']:
            flash("Player 2 not selected!")
        else:
            p1 = request.form['player1']
            s1 = int(request.form['score1'])
            p2 = request.form['player2']
            s2 = int(request.form['score2'])
            d = date.today()

            con = get_db_connection()
            print(p1)
            elo1 = con.execute('SELECT elo FROM players WHERE name=?',(p1,)).fetchone()['elo'] #treating this like char array???
            elo2 = con.execute('SELECT elo FROM players WHERE name=?',(p2,)).fetchone()['elo']

            con.execute("INSERT INTO matches(player1,score1,player2,score2,date) VALUES(?, ?, ?, ?, ?)", (p1, s1, p2, s2, d))
            
            new1,new2 = calculate_elo(s1,s2,elo1,elo2)

            con.execute('UPDATE players SET elo=? WHERE name=?', (new1, p1))
            con.execute('UPDATE players SET elo=? WHERE name=?', (new2, p2))
            
            con.commit()
            con.close()

            return redirect(url_for('index'))
    
    return render_template('match.html', names=get_names())