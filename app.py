import os
import string
import sqlite3
from datetime import date

from dotenv import load_dotenv
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug import exceptions

from elosystem import EloSystem

DATABASE_PATH = 'database.db'
ELO_SYS = EloSystem(100, 50, 10, True)
VALID_CHARS = string.ascii_letters + string.digits + " "
MAX_SCORE = 99

def get_db_connection() -> sqlite3.Connection:
    if os.path.exists(DATABASE_PATH):
        con = sqlite3.connect(DATABASE_PATH)
        con.row_factory = sqlite3.Row
        return con
    else:
        raise Exception("database file not found!")

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

@app.route('/')
def index():
    return redirect(url_for('rankings'))

@app.route('/rankings')
def rankings():
    con = get_db_connection()
    players = con.execute('SELECT * FROM players ORDER BY elo DESC').fetchall()
    con.close()
    return render_template('rankings.html', players=players)

@app.route('/input')
def input():
    con = get_db_connection()
    names = [row['name'] for row in con.execute('SELECT name FROM players').fetchall()]
    con.close()
    return render_template('input.html', names=names)

@app.route('/matches')
def matches():
    con = get_db_connection()
    matches = con.execute('SELECT * FROM matches ORDER BY id DESC').fetchall()
    con.close()
    return render_template('matches.html', matches=matches)

@app.route('/input/player', methods=('GET', 'POST'))
def input_player():
    if request.method == 'POST':
        try:
            name = request.form['name'].strip()
        except exceptions.BadRequestKeyError:
            flash("Form not filled!")
        else:
            if not all([c in VALID_CHARS for c in name]):
                flash("Invalid characters in name!")
            else:
                con = get_db_connection()
                try:
                    con.execute('INSERT INTO players VALUES (?, ?)', (name, ELO_SYS.default))
                except sqlite3.IntegrityError:
                    flash("Name is taken!")
                else:
                    con.commit()
                    con.close()
                    return redirect(url_for('index'))
                finally:
                    con.close()
    return redirect(url_for('input'))

@app.route('/input/match', methods=('GET', 'POST'))
def input_match():
    if request.method == 'POST':
        print(request.form)
        try: 
            p1 = request.form['player1']
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
                elo1:float = con.execute('SELECT elo FROM players WHERE name=?',(p1,)).fetchone()['elo']
                elo2:float = con.execute('SELECT elo FROM players WHERE name=?',(p2,)).fetchone()['elo']
                new1,new2 = ELO_SYS.calculate_elo(s1,s2,elo1,elo2)
                con.execute(
                    "INSERT INTO matches(player1,score1,player2,score2,date,elochange1,elochange2) VALUES(?, ?, ?, ?, ?, ?, ?)",
                    (p1, s1, p2, s2, date.today(), new1-elo1, new2-elo2)
                )
                con.execute('UPDATE players SET elo=? WHERE name=?', (new1, p1))
                con.execute('UPDATE players SET elo=? WHERE name=?', (new2, p2))
                con.commit()
                con.close()
                return redirect(url_for('index'))
    return redirect(url_for('input'))

@app.route('/players/<player>')
def player_page(player):
    pass