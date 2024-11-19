CREATE TABLE players (
    'name' TEXT PRIMARY KEY,
    'elo' REAL NOT NULL
);

CREATE TABLE matches (
    'id' INTEGER PRIMARY KEY AUTOINCREMENT,
    'player1' TEXT REFERENCES players('name'),
    'score1' INTEGER NOT NULL,
    'elochange1' REAL,
    'player2' TEXT REFERENCES players('name'),
    'score2' INTEGER NOT NULL,
    'elochange2' REAL,
    'date' DATE
);