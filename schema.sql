DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS matches;

CREATE TABLE players (
    'name' TEXT PRIMARY KEY,
    'elo' INTEGER NOT NULL
);

CREATE TABLE matches (
    'id' INTEGER PRIMARY KEY AUTOINCREMENT,
    'player1' TEXT REFERENCES players('name'),
    'score1' INTEGER NOT NULL,
    'player2' TEXT REFERENCES players('name'),
    'score2' INTEGER NOT NULL,
    'date' DATE
);