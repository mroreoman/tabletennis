import sqlite3

con = sqlite3.connect("database.db")

with open('schema.sql') as f:
    con.executescript(f.read())

cur = con.cursor()

player_sample = [("Hector", 1), ("Aryan", 2), ("Nabil", 300), ("Esau", 299)]
cur.executemany("INSERT INTO players VALUES(?, ?)", player_sample)

match_sample = [
    ("Hector", 0, "Aryan", 11),
    ("Aryan", 5, "Hector", 11),
    ("Nabil", 21, "Hector", 17),
    ("Esau", 13, "Nabil", 21)
]
cur.executemany("INSERT INTO matches(player1,score1,player2,score2) VALUES(?, ?, ?, ?)", match_sample)

con.commit()
con.close()