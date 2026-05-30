import sqlite3
import os

DB = "data/rc24.db"

os.makedirs("data", exist_ok=True)


PLAYERS = [
    "Maruti Masters",
    "Demon Slayers",
    "Pampers",
    "Urban Strikers",
    "Dashing Risers",
    "Thunder Buddies",
    "Amarnath",
    "Kanyaraasi",
    "Lightning Stricker",
    "Knight Riders",
]


MATCHES = [
    (1, "Knight Riders", "Maruti Masters"),
    (2, "Demon Slayers", "Lightning Stricker"),
    (3, "Pampers", "Kanyaraasi"),
    (4, "Urban Strikers", "Amarnath"),
    (5, "Dashing Risers", "Thunder Buddies"),

    (6, "Knight Riders", "Demon Slayers"),
    (7, "Pampers", "Maruti Masters"),
    (8, "Urban Strikers", "Lightning Stricker"),
    (9, "Dashing Risers", "Kanyaraasi"),
    (10, "Thunder Buddies", "Amarnath"),

    (11, "Knight Riders", "Pampers"),
    (12, "Urban Strikers", "Demon Slayers"),
    (13, "Dashing Risers", "Maruti Masters"),
    (14, "Thunder Buddies", "Lightning Stricker"),
    (15, "Amarnath", "Kanyaraasi"),

    (16, "Knight Riders", "Urban Strikers"),
    (17, "Dashing Risers", "Pampers"),
    (18, "Thunder Buddies", "Demon Slayers"),
    (19, "Amarnath", "Maruti Masters"),
    (20, "Kanyaraasi", "Lightning Stricker"),

    (21, "Knight Riders", "Dashing Risers"),
    (22, "Thunder Buddies", "Urban Strikers"),
    (23, "Amarnath", "Pampers"),
    (24, "Kanyaraasi", "Demon Slayers"),
    (25, "Lightning Stricker", "Maruti Masters"),
]


def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # Matches table
    c.execute("""
    CREATE TABLE IF NOT EXISTS matches(
        id INTEGER PRIMARY KEY,
        p1 TEXT,
        p2 TEXT,
        s1 INTEGER,
        s2 INTEGER,
        done INTEGER DEFAULT 0
    )
    """)

    # Standings table
    c.execute("""
    CREATE TABLE IF NOT EXISTS standings(
        player TEXT PRIMARY KEY,
        played INTEGER DEFAULT 0,
        win INTEGER DEFAULT 0,
        loss INTEGER DEFAULT 0,
        tie INTEGER DEFAULT 0,
        pts INTEGER DEFAULT 0,
        rrd INTEGER DEFAULT 0
    )
    """)

    # Insert players
    for player in PLAYERS:
        c.execute(
            """
            INSERT OR IGNORE INTO standings(player)
            VALUES(?)
            """,
            (player,),
        )

    # Insert matches
    for match in MATCHES:
        c.execute(
            """
            INSERT OR IGNORE INTO matches(id,p1,p2)
            VALUES(?,?,?)
            """,
            match,
        )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("RC24 database created successfully")