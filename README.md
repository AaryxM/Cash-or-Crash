# Cash-or-Crash
# 🍹 Cash or Crash: Summer Juice Stand

A cozy summer café/juice stand themed game built with **Python**, **Tkinter**, and **SQLite**.  
You play as a cat running a refreshment stand during the hottest summer ever. Customers arrive with drink orders, and your job is to prepare them correctly. Serve drinks well to earn cash. Mess up and you lose money. At the end of the day, pay supplies cost and see if your stand survives or crashes!

---

## 🎮 Features
- Intro cutscene with summer café vibe
- Customer orders with cute sprites
- Drink-making mini-game (select correct ingredients)
- Balance system: earn cash for correct drinks, lose cash for mistakes
- End-of-day rent deduction (Cash or Crash!)
- SQLite database integration:
  - Track players, scores, and orders
  - Save high scores and progress
- Cozy theme with pastel backgrounds, playful fonts, and optional sound effects

---

## 🛠️ Requirements
- Python 3.x
- Tkinter (built-in with Python)
- SQLite (`sqlite3` module, built-in with Python)
- Optional: `pygame` for sound effects

---

## 📂 Project Structure
\\\
cash_or_crash/
│── main.py              # Entry point
│── ui.py                # Tkinter windows, menus, gameplay screens
│── db.py                # SQLite database setup & queries
│── game_logic.py        # Drink recipes, scoring, economy
│── assets/
│   ├── images/          # Backgrounds, sprites, ingredient icons
│   └── sounds/          # Audio effects (optional)
│── game.db              # SQLite database file
│── README.md            # Project documentation
\\\
## 🗄️ Database (SQLite)

The game stores its data in `game.db`, managed by `db.py`. The tables are created
automatically the first time the game starts, so no setup is needed.

### Tables

| Table | Purpose | Main columns |
|-------|---------|--------------|
| `players` | One row per player run | `id` (PK), `name`, `balance`, `score` |
| `game_sessions` | One row per play-through | `id` (PK), `player_id` (FK), `days_survived`, `final_score`, `final_balance`, `started_at`, `ended_at` |
| `orders` | Every customer order served | `id` (PK), `drink_name`, `success`, `timestamp`, `player_id` (FK), `session_id` (FK) |
| `drinks` | The drinks menu and recipes | `id` (PK), `name` (unique), `price`, `ingredients` |

**Relationships:** a player has many sessions, and a session has many orders
(`game_sessions.player_id → players.id`, `orders.player_id → players.id`,
`orders.session_id → game_sessions.id`).

### How the game uses it

1. **Launch:** `init_db()` creates the tables and `seed_drinks()` fills the menu from the recipes.
2. **START:** the player's name is saved (`save_player`) and a session begins (`start_session`).
3. **CHECK ORDER:** each order is saved with its result (`save_order`).
4. **Game over / closing the window:** the final balance and score are saved (`update_player`, `end_session`).
5. **HIGH SCORES:** the top 5 players are read with `get_high_scores`.

### Useful queries

```sql
-- Top 5 scores
SELECT name, score FROM players ORDER BY score DESC LIMIT 5;

-- How often each drink was ordered and made correctly
SELECT drink_name, COUNT(*) AS ordered, SUM(success) AS correct
FROM orders GROUP BY drink_name;

-- Orders per player
SELECT p.name, COUNT(o.id) AS orders
FROM players p JOIN orders o ON o.player_id = p.id
GROUP BY p.name;
```

Open `game.db` with [DB Browser for SQLite](https://sqlitebrowser.org/) to look at the data.
