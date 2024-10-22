import sqlite3

con = sqlite3.connect("database.db")

with open('schema.sql') as f:
    con.executescript(f.read())

cur = con.cursor()

data = [("Hector", 1), ("Aryan", 1.1), ("Nabil", 300), ("Esau", 299.9999)]
cur.executemany("INSERT INTO players VALUES(?, ?)", data)

con.commit()
con.close()