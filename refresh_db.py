import os
import sys
import sqlite3

import app

if len(sys.argv) > 1 and "-schema" in sys.argv:
    con = sqlite3.connect(app.DATABASE_PATH)
    if os.path.exists(app.DATABASE_PATH):
        if input("database file already exists. drop tables to update schema (enter y/yes)? ") in ("y", "yes"):
            print("clearing " + app.DATABASE_PATH)
            con.execute("DROP TABLE IF EXISTS players")
            con.execute("DROP TABLE IF EXISTS matches")
            con.commit()
    print("creating database with new schema at " + app.DATABASE_PATH)
    with open('schema.sql') as f:
        con.executescript(f.read())
    con.commit()
    con.close()

if len(sys.argv) > 1 and "-elo" in sys.argv:
    print("recalculating elos in " + app.DATABASE_PATH)
    con = app.get_db_connection()
    elo_sys = app.ELO_SYS

    #reset player elos
    players = con.execute('SELECT * FROM players').fetchall()
    for player in players:
        con.execute('UPDATE players SET elo=? WHERE name=?', (elo_sys.default, player['name']))
    con.commit()

    #recalculate elos
    matches = con.execute('SELECT * FROM matches ORDER BY id ASC').fetchall()
    for match in matches:
        p1:str = match['player1']
        s1:int = match['score1']
        p2:str = match['player2']
        s2:int = match['score2']

        elo1:float = con.execute('SELECT elo FROM players WHERE name=?',(p1,)).fetchone()['elo']
        elo2:float = con.execute('SELECT elo FROM players WHERE name=?',(p2,)).fetchone()['elo']
        new1,new2 = elo_sys.calculate_elo(s1,s2,elo1,elo2)
        con.execute('UPDATE players SET elo=? WHERE name=?', (new1, p1))
        con.execute('UPDATE players SET elo=? WHERE name=?', (new2, p2))
        con.execute('UPDATE matches SET elochange1=?, elochange2=? WHERE id=?', (new1-elo1, new2-elo2, match['id']))
        con.commit()
    con.close()