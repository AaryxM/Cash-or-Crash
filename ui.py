import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from db import (
    save_order,
    # --- DB additions ---
    init_db,
    seed_drinks,
    save_player,
    update_player,
    start_session,
    end_session,
    get_high_scores,
)

from game_logic import (
    get_random_order,
    check_order,
    update_balance,
    end_day,
    get_summary,
    calculate_score,
    recipes
)

colors = {
    "cream": "#FFF9ED",
    "paper": "#FFFDF7",
    "coral": "#E37162",
    "coral_dark": "#A94F48",
    "brown": "#e4bb8f",
    "brown_dark": "#bd8361",
    "muted": "#d59f70",
    "sky": "#A9DCE0",
    "yellow_light": "#fbf4df",
    "green": "#79A66E",
    "counter": "#B9764D",

}

class CashOrCrashApp(tk.Tk):
    #passing in tk.Tk so that this whole class itself is the main window.
    def __init__(self):
        super().__init__()
        self.configure(bg=colors["cream"])
        # self.wm_attributes('-transparentcolor', self['bg'])

        self.geometry('2114x1321')
        # self.session: GameSession | None = None

        # self.attributes("-fullscreen", True)

        # --- DB: create the tables + fill the drinks menu (safe to run every launch)
        init_db()
        seed_drinks([(name, 10, ",".join(items)) for name, items in recipes.items()])

        # --- DB: current game state (filled in when START is pressed)
        self.player_id = None
        self.session_id = None
        self.game_active = False
        self.days = 0

        # --- DB: if the window is closed mid-game, still save the progress
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # --- DB: saves the final balance/score so the high scores table is correct
    def save_progress(self):
        if not self.game_active:
            return
        self.game_active = False
        score = calculate_score(self.orders)
        update_player(self.player_id, self.current_balance, score)
        end_session(self.session_id, self.days, score, self.current_balance)

    def on_close(self):
        self.save_progress()
        self.destroy()

    # --- DB: popup with the top 5 scores (read from the players table)
    def show_high_scores(self):
        popup = tk.Toplevel(self)
        popup.title("High Scores")
        popup.configure(bg=colors["cream"])
        popup.geometry("420x360")

        tk.Label(
            popup,
            text="HIGH SCORES",
            font=("retro_font", 18, "bold"),
            bg=colors["cream"],
            fg=colors["coral"]
        ).pack(pady=15)

        scores = get_high_scores(5)
        if not scores:
            tk.Label(popup, text="No scores yet - be the first!",
                     font=("retro_font", 12), bg=colors["cream"],
                     fg=colors["brown_dark"]).pack(pady=10)
        for rank, (name, balance, score) in enumerate(scores, start=1):
            tk.Label(
                popup,
                text=f"{rank}.  {name}   -   {score} pts   (${balance})",
                font=("retro_font", 13),
                bg=colors["cream"],
                fg=colors["brown_dark"]
            ).pack(pady=3)

        tk.Button(
            popup, text="CLOSE",
            font=("retro_font", 12, "bold"),
            bg=colors["coral"], fg="white",
            command=popup.destroy
        ).pack(pady=20)

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
        bgimg = Image.open("./assets/bg_img.jpeg")
        bgimg = bgimg.rotate(270)
        bgimg = bgimg.resize((1500, 1505))

        self.bg_img = ImageTk.PhotoImage(bgimg)

        background_label = tk.Label(self, image=self.bg_img)

        background_label.place(relwidth=1, relheight=1)

        # game logo ⚒️🛠️

        logoimg = Image.open("game_logo.png").convert("RGBA")
        logoimg = logoimg.resize((800, 350))

        self.logo_img = ImageTk.PhotoImage(logoimg)

        logo_label = tk.Label(self, image=self.logo_img)

        logo_label.pack()

        # --- DB: player name box (saved in the players table)
        tk.Label(
            self,
            text="ENTER YOUR NAME",
            background=colors["cream"],
            foreground=colors["coral"],
            font=("retro_font", 14, "bold"),
        ).pack(pady=(20, 5))

        self.name_entry = tk.Entry(
            self,
            font=("retro_font", 16),
            justify="center",
            width=20,
        )
        self.name_entry.pack(pady=(0, 20))

        start_btn = ttk.Button(
            self,text="START",
            style="Coral.TButton",
            command=self.start_new_game      # was self.show_game
        )
        start_btn.pack(anchor='s')

        # --- DB: opens the high score list
        tk.Button(
            self, text="HIGH SCORES",
            font=("retro_font", 12, "bold"),
            bg=colors["brown_dark"], fg="white",
            padx=20, pady=8,
            command=self.show_high_scores
        ).pack(pady=15)

    # --- DB: called when START is pressed - creates the player + session rows
    def start_new_game(self):
        player_name = self.name_entry.get().strip() or "Player"

        self.show_game()          # builds the screen and sets the starting balance

        self.player_id = save_player(player_name, self.current_balance, 0)
        self.session_id = start_session(self.player_id)
        self.days = 0
        self.game_active = True

    def show_game(self):
        self.clear_windows()

        # headers with the current session details!
        header = tk.Frame(
            self,
            bg=colors["paper"],
            padx=35,
            pady=15
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
        self.orders = []

        self.order_label = tk.Label(header,text=f"CUSTOMER ORDER: {self.current_order}",
            background=colors["paper"],foreground=colors["brown"],
            font=("retro_font", 18, "bold"))
        self.order_label.pack(side="left", padx=50)

        # 🛠️⚒️ connect to db for current session's balance.
        self.current_balance = 10
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
        _stand = Image.open('./assets/stand.png')
        _stand = _stand.resize((1500, 780))

        self.stand_img = ImageTk.PhotoImage(_stand)

        stand_label = tk.Label(self,image=self.stand_img,background=colors["sky"])

        stand_label.pack(side="top")

        # Ingredient selection
        self.selected_ingredients = []

        ingredients = ["watermelon","milk","ice","lemon","sugar","water","orange", "mint"]
        ingredients_pics = ['./assets/watermelon.png','./assets/milk.png','./assets/ice.png','./assets/lemon.png','./assets/sugar.png','./assets/water.png','./assets/orange.png', './assets/mint.png']

        ingredients = ["watermelon", "ice", "lemon", "sugar", "orange", "mint"]
        self.ingredient_images = {}
        self.ingredient_buttons = {}

        for ingredient in ingredients:
            image = Image.open(f"./assets/{ingredient}.png")
            #thumbnail to maintain the size ratio
            image.thumbnail((230, 230))
            self.ingredient_images[ingredient] = ImageTk.PhotoImage(image)

            button = tk.Button(
                self,
                image=self.ingredient_images[ingredient],
                # bg=colors["yellow"],
                bg=colors["brown"],
                height = 100,
                width= 140,
                padx=0,
                pady=0,
                relief = "flat",
                command=lambda item=ingredient: self.select_ingredient(item),
            )
            self.ingredient_buttons[ingredient] = button

            check_button = tk.Button(
            self,text="CHECK ORDER",font=("retro_font", 14, "bold"),
            bg=colors["coral"],fg="white",
            padx=25,pady=10,command=self.check_current_order)

            check_button.place(relx=0.5,rely=0.95,anchor="center")

            end_day_button = tk.Button(
            self,text="END DAY",font=("retro_font", 12, "bold"),
            bg=colors["brown"],fg="white",
            padx=20,pady=8,command=self.finish_day)

            end_day_button.place(relx=0.85,rely=0.95,anchor="center")

            self.result_label = tk.Label(self,text="",
            background=colors["brown_dark"],foreground=colors["brown"],
            font=("retro_font", 18, "bold"))

            self.result_label.place(relx=0.5,rely=0.78,anchor="center")

        self.ingredient_buttons['watermelon'].place(x = 110, y = 580)
        self.ingredient_buttons['orange'].place(x = 315, y= 580)
        self.ingredient_buttons['lemon'].place(x = 515, y = 580)
        self.ingredient_buttons['mint'].place(x = 110, y = 710)
        self.ingredient_buttons['ice'].place(x = 315, y = 710)
        self.ingredient_buttons['sugar'].place(x = 515, y = 710)

        image = Image.open(f"./assets/milk.png")
        image.thumbnail((230, 230))
        self.ingredient_images["milk"] = ImageTk.PhotoImage(image)
        milk_button = tk.Button(
            self,
            image=self.ingredient_images["milk"],
            # bg=colors["yellow"],
            bg=colors["brown_dark"],
            height = 130,
            width= 100,
            padx=0,
            pady=0,
            relief = "flat",
            command=lambda item="milk": self.select_ingredient(item),
        )
        self.ingredient_buttons["milk"] = milk_button
        self.ingredient_buttons['milk'].place(x = 0, y = 550)

        image = Image.open(f"./assets/water.png")
        image.thumbnail((230, 230))
        self.ingredient_images["water"] = ImageTk.PhotoImage(image)
        water_button = tk.Button(
            self,
            image=self.ingredient_images["water"],
            # bg=colors["yellow"],
            bg=colors["brown_dark"],
            height = 130,
            width= 100,
            padx=0,
            pady=0,
            relief = "flat",
            command=lambda item="water": self.select_ingredient(item),
        )
        self.ingredient_buttons["water"] = water_button
        self.ingredient_buttons['water'].place(x = 0, y = 700)


    def select_ingredient(self, ingredient):
        if ingredient not in self.selected_ingredients:
            self.selected_ingredients.append(ingredient)
            print("Selected:", self.selected_ingredients)

            self.ingredient_buttons[ingredient].config(bg=colors["muted"])

    # checks if the selected ingredients match the recipe for the current order and updates the balance accordingly.
    def check_current_order(self):
        success = check_order(self.current_order,self.selected_ingredients)            
        # --- DB: the order is now saved with the player and session it belongs to
        save_order(self.current_order, success, self.player_id, self.session_id)
        self.orders.append({"drink": self.current_order,"success": success})

        # Update balance
        self.current_balance = update_balance(self.current_balance,success)
        self.balance.config(text=f"BALANCE: ${self.current_balance}")

        # Show result
        if success:
            result_text = "✓ CORRECT ORDER! +$10"
            result_color = colors["green"]
        else:
            result_text = "✗ WRONG ORDER! -$5"
            result_color = colors["coral"]

        self.result_label.config(text=result_text,foreground=result_color)

        print(result_text)
        print("Current balance:", self.current_balance)

        if self.current_balance<0:
            self.show_game_over()
        else:
        # Wait 1 second, then start the next order
            self.after(1000, self.start_next_order)

    def show_game_over(self):
        # --- DB: save final balance, score and session before the screen changes
        self.save_progress()

        # Clear the window
        self.clear_windows()

        # Load and display a "Game Over" image
        gameover_img = Image.open("./assets/gameover.png").resize((1000, 600))
        self.gameover_img = ImageTk.PhotoImage(gameover_img)

        gameover_label = tk.Label(self, image=self.gameover_img, bg=colors["cream"])
        gameover_label.pack(expand=True)
        self.configure(bg = colors["yellow_light"])

        # Optional: add a restart button
        restart_btn = ttk.Button(
            self,
            text="RESTART",
            style="Coral.TButton",
            command=self.intro
        )
        restart_btn.pack(pady=20)

        # --- DB: the player can see how they ranked
        tk.Button(
            self, text="HIGH SCORES",
            font=("retro_font", 12, "bold"),
            bg=colors["brown_dark"], fg="white",
            padx=20, pady=8,
            command=self.show_high_scores
        ).pack(pady=5)

        
    # function to run in a loop
    def start_next_order(self):
        # Generate a new customer order
        self.current_order = get_random_order()

        # Update customer order on screen
        self.order_label.config(text=f"CUSTOMER ORDER: {self.current_order}")

        # Reset selected ingredients
        self.selected_ingredients = []

        # Reset ingredient buttons to yellow
        for button in self.ingredient_buttons.values():
            button.config(bg=colors["brown"])

        # Clear previous result
        self.result_label.config(text="")

        print("Next order:", self.current_order)

    # def finish_day(self):
    #     final_balance = end_day(self.current_balance)

    #     # Update balance
    #     self.current_balance = final_balance

    #     self.balance.config(text=f"BALANCE: ${self.current_balance}")

    #     print("End of day!")
    #     print("Rent: $30")
    #     print("Final balance:", self.current_balance)

    def finish_day(self):
        final_balance = end_day(self.current_balance)
        if final_balance >= 0:
            self.days += 1      # --- DB: only a day that was survived counts in game_sessions.days_survived

        # Update balance
        self.current_balance = final_balance
        self.balance.config(text=f"BALANCE: ${self.current_balance}")

        # Create popup window
        popup = tk.Toplevel(self)
        popup.title("End of Day Summary")
        popup.configure(bg=colors["cream"])
        popup.geometry("400x250")

        # Heading
        tk.Label(
            popup,
            text="End of Day Report",
            font=("retro_font", 18, "bold"),
            bg=colors["cream"],
            fg=colors["coral"]
        ).pack(pady=15)

        # Rent and balance info
        tk.Label(
            popup,
            text="Rent: $30",
            font=("retro_font", 14),
            bg=colors["cream"],
            fg=colors["brown"]
        ).pack(pady=5)

        tk.Label(
            popup,
            text=f"Final Balance: ${self.current_balance}",
            font=("retro_font", 14, "bold"),
            bg=colors["cream"],
            fg=colors["green"] if self.current_balance > 0 else colors["coral"]
        ).pack(pady=5)

        # Close button
        tk.Button(
            popup,
            text="OK",
            font=("retro_font", 12, "bold"),
            bg=colors["coral"],
            fg="white",
            command=lambda: self.close_day_popup(popup)    # was popup.destroy
        ).pack(pady=20)

        print("End of day!")
        print("Rent: $30")
        print("Final balance:", self.current_balance)

    # --- if the rent can't be paid (balance below 0) the stand crashes
    def close_day_popup(self, popup):
        popup.destroy()
        if self.current_balance < 0:
            self.show_game_over()

        

    def draw_intro():
        pass

    def show_result():
        pass

# only start the game when this file is run directly
if __name__ == "__main__":
    c = CashOrCrashApp()
    c.intro()
    c.mainloop()
