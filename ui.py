import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from game_logic import (
    get_random_order,
    check_order,
    update_balance,
    end_day,
    get_summary,
    recipes
)

colors = {
    "cream": "#FFF9ED",
    "paper": "#FFFDF7",
    "coral": "#E37162",
    "coral_dark": "#A94F48",
    "brown": "#604432",
    "muted": "#987B65",
    "sky": "#A9DCE0",
    "yellow": "#F5CD69",
    "green": "#79A66E",
    "counter": "#B9764D",
}

class CashOrCrashApp(tk.Tk):
    #passing in tk.Tk so that this whole class itself is the main window.
    def __init__(self):
        super().__init__()
        self.configure(bg=colors["cream"])

        self.geometry('2114x1321')
        # self.session: GameSession | None = None

        # self.attributes("-fullscreen", True)

    def config_styles(self):
        #---for basic styling
        style = ttk.Style(self)
        style.theme_use("clam")
        #style.configure(stylederivedname, font, fg, padding)
        style.configure(
            "Coral.TButton",
            font=("retro_font", 12, "bold"),
            foreground="white",
            background=colors["coral"],
            padding=(100, 30),
        )
        style.map(
            "Coral.TButton",
            foreground=[("active", colors["paper"])],
            background=[("active", colors["coral_dark"])]
        )

    def clear_windows(self):
        for small_window in self.winfo_children():
            small_window.destroy()

    # Intro interface
    def intro(self):
        # displays the intro screen with game title, description, and name entry.

        self.clear_windows()
        # C = Canvas(root, height, width, bd, bg, ..)
        # canvas = tk.Canvas(self, bg = colors["sky"], bd = 0)

        # 🏖️bg image
        self.config_styles()
        bgimg = Image.open("bg_img2.png")
        bgimg = bgimg.resize((1800, 915))

        self.bg_img2 = ImageTk.PhotoImage(bgimg)

        background_label = tk.Label(self, image=self.bg_img2)

        background_label.place(relwidth=1, relheight=1)

        # game logo ⚒️🛠️

        logoimg = Image.open("game_logo.png")
        logoimg = logoimg.resize((700, 350))

        self.logo_img = ImageTk.PhotoImage(logoimg)

        logo_label = tk.Label(self, image=self.logo_img)

        logo_label.pack()

        start_btn = ttk.Button(
            self,
            text="START",
            style="Coral.TButton",
            command=self.show_game
        )
        start_btn.pack(anchor='s')

    def show_game(self):
        self.clear_windows()

        # headers with the current session details!
        header = tk.Frame(
            self,
            bg=colors["paper"],
            padx=35,
            pady=30
        )

        header.pack(side="top", fill='both')

        tk.Label(
            header,
            text="Cash or Crash",
            background=colors["paper"],
            foreground=colors["coral"],
            font=("retro_font", 18, "bold"),
        ).pack(side="left")

        # Get a random customer order
        self.current_order = get_random_order()

        tk.Label(
            header,
            text=f"CUSTOMER ORDER: {self.current_order}",
            background=colors["paper"],
            foreground=colors["brown"],
            font=("retro_font", 18, "bold")
        ).pack(side="left", padx=50)

        # 🛠️⚒️ connect to db for current session's balance.
        self.current_balance = 100
        bal = self.current_balance

        self.balance = tk.Label(
            header,
            text=f"BALANCE: ${bal}",
            background=colors["paper"],
            foreground=colors["brown"],
            font=("retro_font", 18, "bold"),
            justify="left"
        )

        self.balance.pack(side="right")

        # Stand image
        _stand = Image.open("stand_img.png")
        _stand = _stand.resize((1700, 900))

        self.stand_img = ImageTk.PhotoImage(_stand)

        stand_label = tk.Label(self,image=self.stand_img,background=colors["sky"])

        stand_label.pack(side="top")

        # Ingredient selection
        self.selected_ingredients = []

        ingredients = ["mango","milk","ice","lemon","sugar","water","tea"]

        ingredient_frame = tk.Frame(self,bg=colors["cream"])

        ingredient_frame.place(relx=0.5,rely=0.88,anchor="center")

        self.ingredient_buttons = {}

        for ingredient in ingredients:
            button = tk.Button(
                ingredient_frame,
                text=ingredient.title(),
                font=("retro_font", 12, "bold"),
                bg=colors["yellow"],
                fg=colors["brown"],
                padx=12,
                pady=6,
                command=lambda item=ingredient: self.select_ingredient(item)
            )

            button.pack(side="left", padx=3)
            self.ingredient_buttons[ingredient] = button

            check_button = tk.Button(
            self,text="CHECK ORDER",font=("retro_font", 14, "bold"),
            bg=colors["coral"],fg="white",
            padx=25,pady=10,
            command=self.check_current_order)

            check_button.place(relx=0.5,rely=0.95,anchor="center")

            self.result_label = tk.Label(self,text="",
            background=colors["cream"],foreground=colors["brown"],
            font=("retro_font", 18, "bold"))

            self.result_label.place(relx=0.5,rely=0.78,anchor="center")

    def select_ingredient(self, ingredient):
        if ingredient not in self.selected_ingredients:
            self.selected_ingredients.append(ingredient)
            print("Selected:", self.selected_ingredients)

            self.ingredient_buttons[ingredient].config(bg=colors["green"])

    # checks if the selected ingredients match the recipe for the current order and updates the balance accordingly.
    def check_current_order(self):
        success = check_order(
            self.current_order,
            self.selected_ingredients
        )

        current_balance = 100

        if hasattr(self, "current_balance"):
            current_balance = self.current_balance

        self.current_balance = update_balance(current_balance,success)

        self.balance.config(text=f"BALANCE: ${self.current_balance}")

        if success:
            result_text = "✓ CORRECT ORDER! +$10"
            result_color = colors["green"]
        else:
            result_text = "✗ WRONG ORDER! -$5"
            result_color = colors["coral"]

        self.result_label.config(text=result_text,foreground=result_color)

        print(result_text)
        
        print("Current balance:", self.current_balance)

        self.result_label = tk.Label(self,text="",background=colors["cream"],
        foreground=colors["brown"],font=("retro_font", 18, "bold"))

        self.result_label.place(relx=0.5,rely=0.78,anchor="center")

    def draw_intro():
        pass

    def show_result():
        pass

c = CashOrCrashApp()
c.intro()
c.mainloop()