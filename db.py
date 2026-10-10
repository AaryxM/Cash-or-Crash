import sqlite3
import hashlib
import secrets


DB_NAME = "game.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        200_000
    ).hex()

    return salt, password_hash


def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()

        # 1. User accounts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL COLLATE NOCASE UNIQUE,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. Player profiles
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                balance INTEGER DEFAULT 100,
                score INTEGER DEFAULT 0,
                user_id INTEGER UNIQUE,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # 3. Individual drink orders
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                drink_name TEXT,
                success INTEGER CHECK(success IN (0, 1)),
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                player_id INTEGER,
                session_id INTEGER
            )
        """)

        # 4. Game sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                start_balance INTEGER,
                end_balance INTEGER,
                total_orders INTEGER DEFAULT 0,
                correct_orders INTEGER DEFAULT 0,
                started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                ended_at DATETIME,
                FOREIGN KEY (player_id) REFERENCES players(id)
            )
        """)

        # Migrate existing databases without deleting old records.
        # CREATE TABLE IF NOT EXISTS does not add columns to old tables.
        player_columns = {
            row[1] for row in cursor.execute(
                "PRAGMA table_info(players)"
            ).fetchall()
        }

        if "user_id" not in player_columns:
            cursor.execute("""
                ALTER TABLE players
                ADD COLUMN user_id INTEGER REFERENCES users(id)
            """)

        order_columns = {
            row[1] for row in cursor.execute(
                "PRAGMA table_info(orders)"
            ).fetchall()
        }

        if "player_id" not in order_columns:
            cursor.execute("""
                ALTER TABLE orders
                ADD COLUMN player_id INTEGER REFERENCES players(id)
            """)

        if "session_id" not in order_columns:
            cursor.execute("""
                ALTER TABLE orders
                ADD COLUMN session_id INTEGER REFERENCES game_sessions(id)
            """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_orders_player
            ON orders(player_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_player
            ON game_sessions(player_id)
        """)


def register_user(username, password):
    username = username.strip()

    if len(username) < 3:
        return False, "Username must have at least 3 characters."

    if len(username) > 30:
        return False, "Username must not exceed 30 characters."

    if len(password) < 8:
        return False, "Password must have at least 8 characters."

    salt, password_hash = hash_password(password)

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO users (username, password_hash, salt)
                VALUES (?, ?, ?)
            """, (username, password_hash, salt))

            user_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO players (name, balance, score, user_id)
                VALUES (?, 100, 0, ?)
            """, (username, user_id))

        return True, "Registration successful!"

    except sqlite3.IntegrityError:
        return False, "That username is already registered."


def authenticate_user(username, password):
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, password_hash, salt
            FROM users
            WHERE username = ? COLLATE NOCASE
        """, (username.strip(),))

        user = cursor.fetchone()

    if user is None:
        return None

    user_id, stored_hash, salt = user
    _, entered_hash = hash_password(password, salt)

    if secrets.compare_digest(entered_hash, stored_hash):
        return user_id

    return None


def get_player(user_id):
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, balance, score
            FROM players
            WHERE user_id = ?
        """, (user_id,))

        return cursor.fetchone()


def save_player(name, balance, score, user_id=None):
    with get_connection() as conn:
        cursor = conn.cursor()

        if user_id is not None:
            cursor.execute("""
                UPDATE players
                SET name = ?, balance = ?, score = ?
                WHERE user_id = ?
            """, (name, balance, score, user_id))

            if cursor.rowcount:
                return

        cursor.execute("""
            INSERT INTO players (name, balance, score, user_id)
            VALUES (?, ?, ?, ?)
        """, (name, balance, score, user_id))


def save_order(drink, success, player_id=None, session_id=None):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO orders
                (drink_name, success, player_id, session_id)
            VALUES (?, ?, ?, ?)
        """, (drink, int(success), player_id, session_id))


def start_session(player_id, balance):
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO game_sessions (player_id, start_balance)
            VALUES (?, ?)
        """, (player_id, balance))

        return cursor.lastrowid


def finish_session(session_id, end_balance):
    with get_connection() as conn:
        conn.execute("""
            UPDATE game_sessions
            SET end_balance = ?,
                ended_at = CURRENT_TIMESTAMP,
                total_orders = (
                    SELECT COUNT(*)
                    FROM orders
                    WHERE session_id = ?
                ),
                correct_orders = (
                    SELECT COUNT(*)
                    FROM orders
                    WHERE session_id = ? AND success = 1
                )
            WHERE id = ?
        """, (
            end_balance,
            session_id,
            session_id,
            session_id
        ))


def get_high_scores():
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name, balance, score
            FROM players
            ORDER BY score DESC, balance DESC
        """)

        return cursor.fetchall()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
