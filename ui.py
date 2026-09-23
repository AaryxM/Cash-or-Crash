import tkinter as tk
from game_logic import get_random_order, check_order, update_balance

# --- Intro Screen ---
class IntroFrame(tk.Frame):
    def __init__(self, master, switch_frame):
        super().__init__(master)
        tk.Label(self, text="☀️ The hottest summer ever!").pack(pady=20)
        tk.Button(self, text="Start Game", command=lambda: switch_frame("MenuFrame")).pack()


# --- Main Menu ---
class MenuFrame(tk.Frame):
    def __init__(self, master, switch_frame):
        super().__init__(master)
        tk.Label(self, text="🍹 Cash or Crash Menu").pack(pady=20)
        tk.Button(self, text="Play", command=lambda: switch_frame("GameFrame")).pack()
        tk.Button(self, text="Instructions", command=lambda: switch_frame("IntroFrame")).pack()
        tk.Button(self, text="Exit", command=master.quit).pack()


# --- Gameplay Screen ---
class GameFrame(tk.Frame):
    def __init__(self, master, switch_frame):
        super().__init__(master)
        self.switch_frame = switch_frame
        self.balance = 0
        self.current_drink = None
        self.chosen_ingredients = []

        self.order_label = tk.Label(self, text="Customer order will appear here")
        self.order_label.pack(pady=10)

        # Ingredient buttons
        self.ingredients = ["mango", "milk", "ice", "lemon", "sugar", "water", "tea"]
        for ing in self.ingredients:
            tk.Button(self, text=ing, command=lambda i=ing: self.add_ingredient(i)).pack(side="left", padx=5)

        tk.Button(self, text="Serve Drink", command=self.serve_drink).pack(pady=20)

        self.result_label = tk.Label(self, text="")
        self.result_label.pack(pady=10)

        tk.Button(self, text="End Day", command=lambda: switch_frame("EndFrame")).pack()

    def add_ingredient(self, ingredient):
        self.chosen_ingredients.append(ingredient)

    def serve_drink(self):
        self.current_drink = get_random_order()
        self.order_label.config(text=f"Customer wants: {self.current_drink}")

        success = check_order(self.current_drink, self.chosen_ingredients)
        self.balance = update_balance(self.balance, success)

        if success:
            self.result_label.config(text=f"✅ Correct! Balance: {self.balance}")
        else:
            self.result_label.config(text=f"❌ Wrong! Balance: {self.balance}")

        self.chosen_ingredients.clear()


# --- End Screen ---
class EndFrame(tk.Frame):
    def __init__(self, master, switch_frame):
        super().__init__(master)
        tk.Label(self, text="Day Summary").pack(pady=20)
        tk.Button(self, text="Back to Menu", command=lambda: switch_frame("MenuFrame")).pack()
