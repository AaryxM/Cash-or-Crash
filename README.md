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
