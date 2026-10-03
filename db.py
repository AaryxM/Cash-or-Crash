import sqlite3
from contextlib import contextmanager

DB_NAME = "game.db"


@contextmanager
def get_conn():
    """Open a connection, commit on success, roll back on error, always close."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _add_column_if_missing(cursor, table, column, definition):
    """Lets an old game.db (from before these changes) upgrade without being deleted."""
    cursor.execute(f"PRAGMA table_info({table})")
    if column not in [row[1] for row in cursor.fetchall()]:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def init_db():
    with get_conn() as conn:
        cursor = conn.cursor()

        # Players table (original)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                balance INTEGER,
                score INTEGER
            )
        """)

        # Orders table (original)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                drink_name TEXT,
                success INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # NEW: drinks menu (price + recipe)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS drinks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                price INTEGER NOT NULL CHECK (price >= 0),
                ingredients TEXT
            )
        """)

        # NEW: one row per play-through
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                days_survived INTEGER DEFAULT 0,
                final_score INTEGER,
                final_balance INTEGER,
                started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                ended_at DATETIME,
                FOREIGN KEY (player_id) REFERENCES players(id)
            )
        """)

        # NEW: link orders to the player and the session that made them
        _add_column_if_missing(cursor, "orders", "player_id", "INTEGER REFERENCES players(id)")
        _add_column_if_missing(cursor, "orders", "session_id", "INTEGER REFERENCES game_sessions(id)")


# ------------------------- players -------------------------
def save_player(name, balance, score):
    """Insert a new player row. Returns the new player id."""
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO players (name, balance, score) VALUES (?, ?, ?)",
            (name, balance, score))
        return cur.lastrowid


def get_player(player_id=None, name=None):
    """Returns (id, name, balance, score) or None. Looks up by id, otherwise by name (latest)."""
    with get_conn() as conn:
        if player_id is not None:
            return conn.execute(
                "SELECT id, name, balance, score FROM players WHERE id = ?", (player_id,)).fetchone()
        return conn.execute(
            "SELECT id, name, balance, score FROM players WHERE name = ? ORDER BY id DESC LIMIT 1",
            (name,)).fetchone()


def update_player(player_id, balance, score):
    """Save the player's current balance and score (call at end of day / game over)."""
    with get_conn() as conn:
        conn.execute("UPDATE players SET balance = ?, score = ? WHERE id = ?",
                     (balance, score, player_id))


def get_high_scores(limit=None):
    """Returns [(name, balance, score), ...] best score first. limit=None gives everyone."""
    query = "SELECT name, balance, score FROM players ORDER BY score DESC"
    params = ()
    if limit:
        query += " LIMIT ?"
        params = (limit,)
    with get_conn() as conn:
        return conn.execute(query, params).fetchall()


# ------------------------- orders -------------------------
def save_order(drink, success, player_id=None, session_id=None):
    """Log one customer order. The last two arguments are optional, so old calls still work."""
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO orders (drink_name, success, player_id, session_id) VALUES (?, ?, ?, ?)",
            (drink, 1 if success else 0, player_id, session_id))
        return cur.lastrowid


def get_order_stats():
    """Returns (total_orders, correct_orders, success_rate_percent)."""
    with get_conn() as conn:
        total, correct = conn.execute(
            "SELECT COUNT(*), COALESCE(SUM(success), 0) FROM orders").fetchone()
    rate = round(100 * correct / total, 1) if total else 0.0
    return total, correct, rate


def get_drink_stats():
    """Returns [(drink_name, times_ordered, times_correct), ...] most ordered first."""
    with get_conn() as conn:
        return conn.execute("""
            SELECT drink_name, COUNT(*), SUM(success)
            FROM orders GROUP BY drink_name ORDER BY COUNT(*) DESC
        """).fetchall()


# ------------------------- drinks -------------------------
def seed_drinks(drinks):
    """drinks = [(name, price, 'Ice,Lemon,Water'), ...]. Safe to call every launch."""
    with get_conn() as conn:
        conn.executemany(
            "INSERT OR IGNORE INTO drinks (name, price, ingredients) VALUES (?, ?, ?)", drinks)


def get_drinks():
    with get_conn() as conn:
        return conn.execute("SELECT name, price, ingredients FROM drinks ORDER BY price").fetchall()


# ------------------------- sessions -------------------------
def start_session(player_id):
    with get_conn() as conn:
        return conn.execute(
            "INSERT INTO game_sessions (player_id) VALUES (?)", (player_id,)).lastrowid


def end_session(session_id, days_survived, final_score, final_balance):
    with get_conn() as conn:
        conn.execute("""
            UPDATE game_sessions
            SET days_survived = ?, final_score = ?, final_balance = ?, ended_at = CURRENT_TIMESTAMP
            WHERE id = ?""", (days_survived, final_score, final_balance, session_id))


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
