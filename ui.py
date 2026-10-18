import random
import tkinter as tk
from tkinter import ttk,messagebox
from PIL import Image, ImageTk
from db import (
    get_connection,
    save_order,
    register_user,
    authenticate_user,
    get_player,
    start_session,
    finish_session,
    save_player
)

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
    "brown": "#e4bb8f",
    "brown_dark": "#bd8361",
    "muted": "#f4e48d",
    "sky": "#D5FAFD",
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
        self.user_id = None
        self.player_id = None
        self.session_id = None
        self.username = None
        self.day_counter = 1   # fallback if no player found

        # load from DB if a user exists
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, balance, score, day_counter FROM players LIMIT 1")
            player = cursor.fetchone()
            if player:
                self.player_id = player[0]
                self.username = player[1]
                self.current_balance = player[2]
                self.current_score = player[3]
                self.day_counter = player[4]

        self.session_goal = 3 + (self.day_counter - 1) * 2
      # first session requires 3 customers
        self.customers_served = 0

    def config_styles(self):
        
        #---for basic styling
        style = ttk.Style(self)
        style.theme_use("clam")
        # --- Pretty green progress bar style
        style.configure(
            "Green.Horizontal.TProgressbar",
            troughcolor=colors["paper"],   # background of the bar track
            background=colors["green"],    # fill color of the bar
            bordercolor=colors["brown"],   # border around the bar
            lightcolor=colors["green"],    # highlight color
            darkcolor=colors["green"]      # shadow color
        )
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

        start_btn = ttk.Button(
            self,text="START",
            style="Coral.TButton",
            command=self.show_game
        )
        start_btn.pack(anchor='s')
        tutorial_btn = ttk.Button(
            self,
            text="TUTORIAL",
            style="Coral.TButton",
            command=self.tutorial_page
        )
        tutorial_btn.pack(anchor='s', pady=10)


    def login_screen(self):
        self.clear_windows()
        self.config_styles()

        bgimg = Image.open("./assets/bg_img.jpeg")
        bgimg = bgimg.rotate(270)
        bgimg = bgimg.resize((1500, 1505))

        self.login_bg_img = ImageTk.PhotoImage(bgimg)
        tk.Label(self, image=self.login_bg_img).place(
            relwidth=1, relheight=1
        )

        card = tk.Frame(self, bg="#FFFDF7", padx=45, pady=30)
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            card, text="CASH OR CRASH",
            font=("retro_font", 25, "bold"),
            bg="#FFFDF7", fg="#E37162"
        ).pack(pady=(0, 8))

        tk.Label(
            card, text="Welcome back, juice maker!",
            font=("retro_font", 12),
            bg="#FFFDF7", fg="#604432"
        ).pack(pady=(0, 20))

        tk.Label(
            card, text="Username",
            font=("retro_font", 12),
            bg="#FFFDF7", fg="#604432"
        ).pack(anchor="w")

        self.username_entry = tk.Entry(
            card, font=("Arial", 13), width=28
        )
        self.username_entry.pack(pady=(5, 15), ipady=5)

        tk.Label(
            card, text="Password",
            font=("retro_font", 12),
            bg="#FFFDF7", fg="#604432"
        ).pack(anchor="w")

        self.password_entry = tk.Entry(
            card, font=("Arial", 13), width=28, show="*"
        )
        self.password_entry.pack(pady=(5, 20), ipady=5)

        tk.Button(
            card, text="LOGIN",
            font=("retro_font", 12, "bold"),
            bg="#E37162",
            fg="white",
            activebackground=colors["coral_dark"],
            activeforeground="white",
            width=20, 
            pady=8,
            command=self.login_user
        ).pack(pady=5)

        tk.Button(
            card, text="Create a new account",
            font=("retro_font", 10),
            bg="#FFFDF7", fg="#604432",
            relief="flat",
            command=self.registration_screen
        ).pack(pady=(12, 0))

        self.username_entry.focus_set()

    def login_user(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning(
                "Missing details",
                "Please enter your username and password."
            )
            return

        user_id = authenticate_user(username, password)

        if user_id is None:
            messagebox.showerror(
                "Login failed",
                "Incorrect username or password."
            )
            return

        player = get_player(user_id)

        if player is None:
            messagebox.showerror(
                "Error",
                "Player profile could not be found."
            )
            return

        self.user_id = user_id
        self.player_id = player[0]
        self.username = player[1]

        # Retrieve saved data from the database
        self.current_balance = player[2]

        # Score should always equal the balance
        self.current_score = self.current_balance
        self.day_counter = player[4]

        # Keep the database score synchronized with the balance
        save_player(
            self.username,
            self.current_balance,
            self.current_score,
            self.user_id
        )

        # Open the existing START screen
        self.intro()

    def registration_screen(self):
            self.clear_windows()
            self.config_styles()

            bgimg = Image.open("./assets/bg_img.jpeg")
            bgimg = bgimg.rotate(270)
            bgimg = bgimg.resize((1500, 1505))

            self.register_bg_img = ImageTk.PhotoImage(bgimg)
            tk.Label(self, image=self.register_bg_img).place(
                relwidth=1, relheight=1
            )

            card = tk.Frame(self, bg="#FFFDF7", padx=45, pady=25)
            card.place(relx=0.5, rely=0.5, anchor="center")

            tk.Label(
                card, text="JOIN THE JUICE STAND!",
                font=("retro_font", 20, "bold"),
                bg="#FFFDF7", fg="#E37162"
            ).pack(pady=(0, 18))

            tk.Label(
                card, text="Choose a username",
                font=("retro_font", 11),
                bg="#FFFDF7", fg="#604432"
            ).pack(anchor="w")

            self.register_username_entry = tk.Entry(
                card, font=("Arial", 13), width=28
            )
            self.register_username_entry.pack(pady=(5, 12), ipady=5)

            tk.Label(
                card, text="Choose a password (8+ characters)",
                font=("retro_font", 11),
                bg="#FFFDF7", fg="#604432"
            ).pack(anchor="w")

            self.register_password_entry = tk.Entry(
                card, font=("Arial", 13), width=28, show="*"
            )
            self.register_password_entry.pack(pady=(5, 12), ipady=5)

            tk.Label(
                card, text="Confirm password",
                font=("retro_font", 11),
                bg="#FFFDF7", fg="#604432"
            ).pack(anchor="w")

            self.confirm_password_entry = tk.Entry(
                card, font=("Arial", 13), width=28, show="*"
            )
            self.confirm_password_entry.pack(pady=(5, 18), ipady=5)

            tk.Button(
                card, text="REGISTER",
                font=("retro_font", 12, "bold"),
                bg="#E37162", fg="white",
                width=20, pady=8,
                command=self.register_new_user
            ).pack(pady=5)

            tk.Button(
                card, text="Back to login",
                font=("retro_font", 10),
                bg="#FFFDF7", fg="#604432",
                relief="flat",
                command=self.login_screen
            ).pack(pady=(10, 0))

    def register_new_user(self):
        username = self.register_username_entry.get().strip()
        password = self.register_password_entry.get()
        confirm = self.confirm_password_entry.get()

        if password != confirm:
            messagebox.showerror(
                "Password mismatch",
                "The passwords do not match."
            )
            return

        success, message = register_user(username, password)

        if success:
            messagebox.showinfo("Registration", message)
            self.login_screen()
            self.username_entry.insert(0, username)
        else:
            messagebox.showerror("Registration failed", message)

    def show_game(self):
        self.clear_windows()

        # Track menu window
        self.menu_window = None

        # Bind 'm' key to toggle menu
        self.bind("<m>", self.toggle_menu)

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

        # Progress bar uses the current session goal
        self.progress = ttk.Progressbar(
            header,
            orient="horizontal",
            length=300,
            mode="determinate",
            maximum=self.session_goal,
            style="Green.Horizontal.TProgressbar" 
        )
        self.progress.pack(side="right", padx=20)
        self.progress["value"] = self.customers_served

        self.day_counter_label = tk.Label(
            header,
            text=f"DAY: {self.day_counter}",
            background=colors["paper"],
            foreground=colors["coral"],
            font=("retro_font", 18, "bold")
        )
        self.day_counter_label.pack(side="left", padx=20)



        # Get a random customer order
        self.current_order = get_random_order()
        self.orders = []

        self.customer_images = [
    "assets/customer/customer1_1.png",
    "assets/customer/customer2_2.png",
    "assets/customer/customer3_3.png"]

        self.current_customer = None
        self.customer_img = None

        self.order_label = tk.Label(header,text=f"CUSTOMER ORDER: {self.current_order}",
            background=colors["paper"],foreground=colors["brown"],
            font=("retro_font", 18, "bold"))
        
        self.order_label.pack(side="left", padx=30)

        # Use the balance retrieved during login
        bal = self.current_balance
        self.current_score = self.current_balance

        # Start a database session for this game
        self.session_id = start_session(self.player_id,self.current_balance)

        self.balance = tk.Label(
            header,
            text=f"BALANCE: ${bal}",
            background=colors["paper"],
            foreground=colors["brown"],
            font=("retro_font", 18, "bold"),
            justify="left"
        )
        self.balance.pack(side="right")

        # Load pixel-art menu icon
        _menu = Image.open("assets/menu_icon.png")
        _menu = _menu.resize((70, 50))
        self.menu_img = ImageTk.PhotoImage(_menu)

        menu_icon = tk.Button(
            header,
            image=self.menu_img,
            bg=colors["paper"],
            bd=0,
            relief="flat",
            cursor="hand2",
            activebackground=colors["paper"],
            command=self.show_menu_book
        )

        menu_icon.pack(
            side="right",
            padx=(30, 5)
        )

        # Stand image
        _stand = Image.open('./assets/stand.png')
        _stand = _stand.resize((1500, 780))

        self.stand_img = ImageTk.PhotoImage(_stand)

        stand_label = tk.Label(self,image=self.stand_img,background=colors["sky"])

        stand_label.pack(side="top")
        # Drink display (blank spot on the counter)
        self.drink_label = tk.Label(self, bg="#e7ccb0", bd=0) 
        
        self.drink_label.place(x=950, y=584)   
        self.drink_img = None

        # Customer
        self.customer_label = tk.Label(
            self,
            background=colors["sky"],
            bd=0
        )

        self.customer_label.place(
            relx=0.62,
            rely=0.44,
            anchor="center"
        )

        self.show_customer()

        # Customer order popup
        self.order_popup = tk.Label(
            self,
            text=f"I'd like a\n{self.current_order}!",
            background="#ffe8df",
            foreground=colors["brown"],
            font=("retro_font", 14, "bold"),
            padx=20,
            pady=12,
            bd=0,
            relief="solid",
            justify="center")
        
        self.order_popup.place(
            relx=0.55,
            rely=0.37,
            anchor="center"
        )

        # Ingredient selection
        self.selected_ingredients = []

        ingredients = ["watermelon","milk","ice","lemon","sugar","water","orange", "mint"]
        ingredients_pics = ['./assets/watermelon.png','./assets/milk.png','./assets/ice.png','./assets/lemon.png','./assets/sugar.png','./assets/water.png','./assets/orange.png', './assets/mint.png']

        ingredients = ["watermelon", "ice", "lemon", "sugar", "orange", "mint"]
        self.ingredient_images = {}
        self.ingredient_buttons = {}

        # Orange button
        orange_img = Image.open("./assets/orange.png").resize((200, 200))
        self.ingredient_images["orange"] = ImageTk.PhotoImage(orange_img)

        orange_button = tk.Button(
            self,
            image=self.ingredient_images["orange"],
            bg=colors["brown"],
            relief="flat",
            height= 100,
            width=140,
            command=lambda item="orange": self.select_ingredient(item),
        )
        self.ingredient_buttons["orange"] = orange_button
        self.ingredient_buttons["orange"].place(x=315, y=585)

        # Lemon button
        lemon_img = Image.open("./assets/lemon.png").resize((200, 200))
        self.ingredient_images["lemon"] = ImageTk.PhotoImage(lemon_img)

        lemon_button = tk.Button(
            self,
            image=self.ingredient_images["lemon"],
            bg=colors["brown"],
            relief="flat",
            height= 100,
            width=140,
            command=lambda item="lemon": self.select_ingredient(item),
        )
        self.ingredient_buttons["lemon"] = lemon_button
        self.ingredient_buttons["lemon"].place(x=515, y=585)

        # Ice button
        ice_img = Image.open("./assets/ice.png").resize((100, 100))
        self.ingredient_images["ice"] = ImageTk.PhotoImage(ice_img)

        ice_button = tk.Button(
            self,
            image=self.ingredient_images["ice"],
            bg=colors["brown"],
            relief="flat",
            height= 100,
            width=140,
            command=lambda item="ice": self.select_ingredient(item),
        )
        self.ingredient_buttons["ice"] = ice_button
        self.ingredient_buttons["ice"].place(x=315, y=715)

        # Sugar button
        sugar_img = Image.open("./assets/sugar.png").resize((120, 120))
        self.ingredient_images["sugar"] = ImageTk.PhotoImage(sugar_img)

        sugar_button = tk.Button(
            self,
            image=self.ingredient_images["sugar"],
            bg=colors["brown"],
            relief="flat",
            height= 100,
            width=140,
            command=lambda item="sugar": self.select_ingredient(item),
        )
        self.ingredient_buttons["sugar"] = sugar_button
        self.ingredient_buttons["sugar"].place(x = 520, y = 715)

        # Mint button
        mint_img = Image.open("./assets/mint.png").resize((200, 200))
        self.ingredient_images["mint"] = ImageTk.PhotoImage(mint_img)

        mint_button = tk.Button(
            self,
            image=self.ingredient_images["mint"],
            bg=colors["brown"],
            relief="flat",
            height= 100,
            width=140,
            command=lambda item="mint": self.select_ingredient(item),
        )
        self.ingredient_buttons["mint"] = mint_button
        self.ingredient_buttons["mint"].place(x = 110, y = 715)

        # watermelon button
        watermelon_img = Image.open("./assets/watermelon.png").resize((200, 200))
        self.ingredient_images["watermelon"] = ImageTk.PhotoImage(watermelon_img)

        watermelon_button = tk.Button(
            self,
            image=self.ingredient_images["watermelon"],
            bg=colors["brown"],
            relief="flat",
            height= 100,
            width=140,
            command=lambda item="watermelon": self.select_ingredient(item),
        )
        self.ingredient_buttons["watermelon"] = watermelon_button
        self.ingredient_buttons["watermelon"].place(x = 110, y = 585)

        # milk button
        milk_img = Image.open("./assets/milk.png").resize((200, 200))
        self.ingredient_images["milk"] = ImageTk.PhotoImage(milk_img)

        milk_button = tk.Button(
            self,
            image=self.ingredient_images["milk"],
            bg=colors["brown_dark"],
            relief="flat",
            width = 80,
            height = 110,
            command=lambda item="milk": self.select_ingredient(item),
        )
        self.ingredient_buttons["milk"] = milk_button
        self.ingredient_buttons["milk"].place(x = 0, y = 550)

        # wwater button
        water_img = Image.open("./assets/water.png").resize((150, 150))
        self.ingredient_images["water"] = ImageTk.PhotoImage(water_img)

        water_button = tk.Button(
            self,
            image=self.ingredient_images["water"],
            bg=colors["brown_dark"],
            relief="flat",
            width = 80,
            height = 120,
            command=lambda item="water": self.select_ingredient(item),
        )
        self.ingredient_buttons["water"] = water_button
        self.ingredient_buttons["water"].place(x = 0, y = 700)



        # for ingredient in ingredients:
        #     image = Image.open(f"./assets/{ingredient}.png")
        #     #thumbnail to maintain the size ratio
        #     image.thumbnail((230, 230))
        #     self.ingredient_images[ingredient] = ImageTk.PhotoImage(image)

        #     button = tk.Button(
        #         self,
        #         image=self.ingredient_images[ingredient],
        #         # bg=colors["yellow"],
        #         bg=colors["brown"],
        #         height = 100,
        #         width= 140,
        #         padx=0,
        #         pady=0,
        #         relief = "flat",
        #         command=lambda item=ingredient: self.select_ingredient(item),
        #     )
        #     self.ingredient_buttons[ingredient] = button

        check_button = tk.Button(
            self,
            text="CHECK ORDER",
            font=("retro_font", 14, "bold"),
            bg=colors["coral"],
            activebackground= colors["coral_dark"],
            activeforeground="white",
            fg="white",
            padx=25,
            pady=10,
            command=self.check_current_order)

        check_button.place(relx=0.5,rely=0.95,anchor="center")

        end_day_button = tk.Button(
            self,text="END DAY",font=("retro_font", 12, "bold"),
            bg=colors["brown"],fg="white",
            padx=20,pady=8,command=self.finish_day)

        # end_day_button.place(relx=0.85,rely=0.95,anchor="center")

        self.result_label = tk.Label(self,text="",
            background=colors["brown_dark"],foreground=colors["brown"],
            font=("retro_font", 18, "bold"))

        self.result_label.place(relx=0.5,rely=0.78,anchor="center")
           
        
    def show_drink(self, drink_name):
        # file name like assets/drinks/lemonade.png
        filename = drink_name.lower().replace(" ", "_")
        img = Image.open(f"./assets/drinks/{filename}.png")
        img = img.resize((225, 225), Image.Resampling.LANCZOS)

        # keep a reference on self or Tkinter will garbage-collect the image
        self.drink_img = ImageTk.PhotoImage(img)
        self.drink_label.config(image=self.drink_img)
        

    def clear_drink(self):
        self.drink_label.config(image="")
        self.drink_img = None

    def show_customer(self):
        # Pick a random customer
        self.current_customer = random.choice(self.customer_images)

        # Load customer image
        customer = Image.open(self.current_customer)

        # Resize customer
        customer = customer.resize((460, 295))

        self.customer_img = ImageTk.PhotoImage(customer)

        # Display customer
        self.customer_label.config(image=self.customer_img)

    def select_ingredient(self, ingredient):
    # If ingredient is already selected, unselect it
        if ingredient in self.selected_ingredients:
            self.selected_ingredients.remove(ingredient)

            self.ingredient_buttons[ingredient].config( bg=colors["brown"])
        # Otherwise, select the ingredient
        else:
            self.selected_ingredients.append(ingredient)

            self.ingredient_buttons[ingredient].config( bg=colors["muted"] )
        print("Selected:", self.selected_ingredients)

    # checks if the selected ingredients match the recipe for the current order and updates the balance accordingly.
    def check_current_order(self):
        success = check_order(self.current_order,self.selected_ingredients)

        save_order(self.current_order,success,self.player_id,self.session_id)

        self.orders.append({"drink": self.current_order,"success": success})

        # Update balance
        self.current_balance = update_balance(self.current_balance, self.current_order, success)

        # Score always equals balance
        self.current_score = self.current_balance

        # Update the balance displayed in the header
        self.balance.config(text=f"BALANCE: ${self.current_balance}")

        # Save updated balance and score
        if self.user_id is not None:
            save_player(
                self.username,
                self.current_balance,
                self.current_score,
                self.user_id
            )
      

        # Update score for a correct order
        #if success:
          #  self.current_score += 1

        # Show result
      
        if success:
            price = recipes[self.current_order]["price"]
            result_text = f"✓ CORRECT ORDER! +${price}"
            result_color = colors["green"]
            self.show_drink(self.current_order)
        else:
            penalty = recipes[self.current_order]["price"] - recipes[self.current_order]["price"]*0.5   # or recipes[self.current_order]["penalty"] if you add per‑drink penalties
            result_text = f"✗ WRONG ORDER! -${penalty}"
            result_color = colors["coral"]

        self.result_label.config(
            text=result_text,
            foreground=result_color,
            background=colors["cream"]
        )

        # --- NEW: update progress bar
        self.customers_served += 1
        self.progress["value"] = self.customers_served

        # --- NEW: check if session goal reached
        if self.customers_served >= self.session_goal:
            self.finish_day()
            return

        if self.current_balance < 0:
            self.show_game_over()
        else:
            self.after(1000, self.start_next_order)



        print(result_text)
        print("Current balance:", self.current_balance)
        print("Current score:", self.current_score)

        if self.current_balance < 0:
            self.show_game_over()
        else:
            # Wait 1 second, then start the next order
            self.after(1000, self.start_next_order)



    def show_game_over(self):
       
                    
        # Clear the window
        self.clear_windows()

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE players
                SET day_counter = 1,
                    balance = 10,
                    score = 10
                WHERE id = ?
            """, (self.player_id,))
            conn.commit()

      
     # Reset local state
        self.day_counter = 1
        self.current_balance = 10
        self.current_score = 10
        self.customers_served = 0
        self.session_goal = 3

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

        
    # function to run in a loop
    def start_next_order(self):

        # Generate new order
        self.current_order = get_random_order()

        # Pick a new customer
        self.show_customer()

        # Update customer order popup
        self.order_popup.config(
            text=f"I'd like a\n{self.current_order}!"
        )

        # Update existing order label
        self.order_label.config(
            text=f"CUSTOMER ORDER: {self.current_order}"
        )

        # Reset selected ingredients
        self.selected_ingredients = []

        for button in self.ingredient_buttons.values():
            button.config(
                bg=colors["brown"]
            )

        self.ingredient_buttons["milk"].config(bg=colors["brown_dark"])
        self.ingredient_buttons["water"].config(bg=colors["brown_dark"])

        # Clear previous result
        self.result_label.config(text="")
        self.clear_drink()
        print("Next order:", self.current_order)

    # def sesh_done():
    #             popup.destroy
    #             intro(self)

    def finish_day(self):
        final_balance = end_day(self.current_balance)

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

        def close_and_restart():
            popup.destroy()
            self.session_goal += 2       # increase goal for next session
            self.customers_served = 0    # reset counter
            self.intro()


        # Close button
       
        tk.Button(
            popup,
            text="OK",
            font=("retro_font", 12, "bold"),
            bg=colors["coral"],
            activebackground=colors["coral_dark"],
            fg="white",
            command=close_and_restart   
        ).pack(pady=20)

        print("End of day!")
        print("Rent: $30")
        print("Final balance:", self.current_balance)
        with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE players
                    SET day_counter = day_counter + 1
                    WHERE id = ?
                """, (self.player_id,))
                conn.commit()
    
        # Fetch updated day counter
        cursor.execute("SELECT day_counter FROM players WHERE id = ?", (self.player_id,))
        self.day_counter = cursor.fetchone()[0]


    def show_menu_book(self):
        self.menu_window = tk.Toplevel(self)

        self.menu_window.title("Recipe Book")
        self.menu_window.configure(bg=colors["brown"])

        # Keep recipe book above the game
        self.menu_window.transient(self)
        self.menu_window.grab_set()

        # Recipe book size
        book_width = 977
        book_height = 550

        # Load recipe book image
        book = Image.open("assets/recipe_book.jpg")
        book = book.resize((book_width, book_height))
        self.recipe_book_img = ImageTk.PhotoImage(book)

        # Canvas for image + recipe text
        canvas = tk.Canvas(
            self.menu_window,
            width=book_width,
            height=book_height,
            bg=colors["brown"],
            highlightthickness=0
        )

        canvas.pack()

        # Display book
        canvas.create_image(
            0,
            0,
            image=self.recipe_book_img,
            anchor="nw"
        )


    
        # Close button
        close_button = tk.Button(
            self.menu_window,
            text="CLOSE",
            font=("retro_font", 12, "bold"),
            bg=colors["coral"],
            activebackground=colors["coral_dark"],
            fg="white",
            padx=25,
            pady=7,
            command=self.menu_window.destroy)
        close_button.pack(pady=10)

    def toggle_menu(self, event=None):
        if self.menu_window is None or not self.menu_window.winfo_exists():
            # Open menu
            self.show_menu_book()
        else:
            # Close menu
            self.menu_window.destroy()
            self.menu_window = None

    def tutorial_page(self):
        self.clear_windows()
        self.config_styles()

        tutorial = tk.Frame(self, bg=colors["cream"], padx=40, pady=30)
        tutorial.pack(fill="both", expand=True)

        tk.Label(
            tutorial,
            text="🍹 How to Play Cash or Crash 🍹",
            font=("retro_font", 22, "bold"),
            bg=colors["cream"],
            fg=colors["coral"]
        ).pack(pady=(0, 20))

        # Basic instructions
        instructions = [
            "1. Customers will order a random drink.",
            "2. Select the correct ingredients by clicking the buttons.",
            "3. Press 'CHECK ORDER' to serve the drink.",
            "4. Correct orders earn coins based on drink price.",
            "5. Wrong orders lose coins (half the price of the drink).",
            "6. At the end of the day, rent ($30) is deducted.",
            "7. Each new day increases the number of customers to serve."
            "8. If your balance goes below 0, you crash! (you then have to start over)"
        ]

        for line in instructions:
            tk.Label(
                tutorial,
                text=line,
                font=("retro_font", 14),
                bg=colors["cream"],
                fg=colors["brown"],
                anchor="w",
                justify="left"
            ).pack(anchor="w", pady=5)

        # Example scoring
        tk.Label(
            tutorial,
            text="Example: Orange Cream costs $14. Correct order = +$14, Wrong order = -$7.",
            font=("retro_font", 13, "italic"),
            bg=colors["cream"],
            fg=colors["green"]
        ).pack(pady=(20, 10))

        # Back button
        tk.Button(
            tutorial,
            text="Back to Menu",
            font=("retro_font", 12, "bold"),
            bg=colors["coral"],
            activebackground=colors["coral_dark"],
            fg="white",
            command=self.intro
        ).pack(pady=20)


    def draw_intro():
        pass

    def show_result():
        pass

if __name__ == "__main__":
    from db import init_db

    init_db()
    c = CashOrCrashApp()
    c.intro()
    c.mainloop()