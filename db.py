import sqlite3

DB_NAME = "game.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Players table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            balance INTEGER,
            score INTEGER
        )
    """)

    # Orders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drink_name TEXT,
            success INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def save_player(name, balance, score):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO players (name, balance, score)
        VALUES (?, ?, ?)
    """, (name, balance, score))

    conn.commit()
    conn.close()


def save_order(drink, success):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO orders (drink_name, success)
        VALUES (?, ?)
    """, (drink, success))

    conn.commit()
    conn.close()

def get_high_scores():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, balance, score
        FROM players
        ORDER BY score DESC
    """)

    scores = cursor.fetchall()

    conn.close()

    return scores

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")