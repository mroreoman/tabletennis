import os
import string
import sqlite3
import math
from datetime import date

from dotenv import load_dotenv
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug import exceptions

VALID_CHARS = string.ascii_letters + string.digits + " -'"
MAX_SCORE = 99
ELO_K = 32
ELO_DEFAULT = 100
ELO_MAX = 10000

def get_db_connection() -> sqlite3.Connection:
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    return con

def get_names() -> list[str]:
    con = get_db_connection()
    names = [row['name'] for row in con.execute('SELECT name FROM players').fetchall()]
    con.close()
    return names

def calculate_elo(s1:int, s2:int, elo1:float, elo2:float) -> tuple[float,float]:
    #1=p1 wins, 0=p2 wins
    odds = 1.0 / (1 + math.pow(10, (elo1 - elo2) / 400.0))
    outcome = ((s1-s2) / max(s1,s2) + 1) / 2
    print(f"odds: {odds}")
    print(f"score: {s1} - {s2}")
    print(f"outcome: {outcome}")

    new1 = elo1 + ELO_K * (outcome - odds)
    new2 = elo2 + ELO_K * (odds - outcome)
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
        try:
            name = request.form['name'].strip()
            elo = ELO_DEFAULT if not request.form['elo'] else int(request.form['elo'])
        except exceptions.BadRequestKeyError:
            flash("Form not filled!")
        except ValueError:
            flash("Elo must be an integer!")
        else:
            if name in get_names():
                flash("Name is taken!")
            elif not all([c in VALID_CHARS for c in name]):
                flash("Invalid characters in name!")
            elif elo < 0 or elo > ELO_MAX:
                flash(f"elo must be between 0 and {ELO_MAX}!")
            else:
                con = get_db_connection()
                con.execute('INSERT INTO players VALUES (?, ?)', (name, elo))
                con.commit()
                con.close()
                return redirect(url_for('index'))

    return render_template('player.html', max_elo = ELO_MAX)

@app.route('/match', methods=('GET', 'POST'))
def match():
    if request.method == 'POST':
        print(request.form)
        try: 
            p1:str = request.form['player1']
            s1 = int(request.form['score1'])
            p2 = request.form['player2']
            s2 = int(request.form['score2'])
        except exceptions.BadRequestKeyError:
            flash("Form not filled!")
        except ValueError:
            flash("Scores must be integers!")
        else:
            if request.form['player1'] == request.form['player2']:
                flash("You can't play yourself!")
            elif (not 0 <= s1 <= MAX_SCORE) or (not 0 <= s2 <= MAX_SCORE):
                flash("Invalid score!")
            elif s1 == s2:
                flash("Score can't be tied!")
            else:
                con = get_db_connection()
                print(p1)
                elo1:float = con.execute('SELECT elo FROM players WHERE name=?',(p1,)).fetchone()['elo'] #treating this like char array???
                elo2:float = con.execute('SELECT elo FROM players WHERE name=?',(p2,)).fetchone()['elo']

                con.execute("INSERT INTO matches(player1,score1,player2,score2,date) VALUES(?, ?, ?, ?, ?)", (p1, s1, p2, s2, date.today()))
                
                new1,new2 = calculate_elo(s1,s2,elo1,elo2)

                con.execute('UPDATE players SET elo=? WHERE name=?', (new1, p1))
                con.execute('UPDATE players SET elo=? WHERE name=?', (new2, p2))
                
                con.commit()
                con.close()

                return redirect(url_for('index'))
    
    return render_template('match.html', names=get_names())