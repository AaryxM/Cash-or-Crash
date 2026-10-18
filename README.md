# Cash-or-Crash
# 🍹 Cash or Crash: Summer Juice Stand

A cozy summer juice stand themed game built with **Python**, **Tkinter**, and **SQLite**.  
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
- Cozy theme with pastel backgrounds, playful fonts etc.

---

## 🛠️ Requirements
- Python 3.x
- Tkinter (built-in with Python)
- SQLite (`sqlite3` module, built-in with Python)

---

## 📂 Project Structure
```
cash_or_crash/
│── main.py              # Entry point
│── ui.py                # Tkinter windows, menus, gameplay screens
│── db.py                # SQLite database setup & queries
│── game_logic.py        # Drink recipes, scoring, economy
│── assets/
│   └── images/         # Backgrounds, sprites, ingredient icons
│── game.db              # SQLite database file
│── README.md            # Project documentation

```

# Database

## 🧩 Entities and Attributes

### 1. **Users**
* **id** (PK, AUTOINCREMENT)  
* **username** (TEXT, UNIQUE, case-insensitive)  
* **password_hash** (TEXT)  
* **salt** (TEXT)  
* **created_at** (DATETIME, default = current timestamp)

- Represents registered accounts. Each user has secure credentials.
---
### 2. **Players**
* **id** (PK, AUTOINCREMENT)  
* **name** (TEXT)  
* **balance** (INTEGER, default = 50)  
* **score** (INTEGER, default = 0)  
* **day_counter** (INTEGER, default = 1)  
* **user_id** (FK → Users.id, UNIQUE)

- Represents the in-game profile linked to a user. Tracks progress, balance, and score.

---

### 3. **Orders**
* **id** (PK, AUTOINCREMENT)  
* **drink_name** (TEXT)  
* **success** (INTEGER, must be 0 or 1)  
* **timestamp** (DATETIME, default = current timestamp)  
* **player_id** (FK → Players.id)  
* **session_id** (FK → GameSessions.id)

- Represents individual drink orders made during gameplay. Tracks correctness and timing.
---

### 4. **GameSessions**
* **id** (PK, AUTOINCREMENT)  
* **player_id** (FK → Players.id, NOT NULL)  
* **start_balance** (INTEGER)  
* **end_balance** (INTEGER)  
* **total_orders** (INTEGER, default = 0)  
* **correct_orders** (INTEGER, default = 0)  
* **started_at** (DATETIME, default = current timestamp)  
* **ended_at** (DATETIME)

- Represents a play session. Tracks performance metrics like total and correct orders.
---

## ⚡ Key Points
* **Security**: Passwords are hashed with PBKDF2-HMAC-SHA256 and salted.  
* **Indexes**:  
  - `idx_orders_player` speeds up queries by player_id.  
  - `idx_sessions_player` speeds up queries by player_id in sessions.  
* **Data Integrity**: Foreign keys enforce relationships, ensuring orders and sessions always belong to valid players.
