import random
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from db import save_order

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

        start_btn = ttk.Button(
            self,text="START",
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

        self.customer_images = [
    "assets/customer/customer1_1.png",
    "assets/customer/customer2_2.png",
    "assets/customer/customer3_3.png"]

        self.current_customer = None
        self.customer_img = None

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
        self.drink_label.place(x=950, y=600)   
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
        
    def show_drink(self, drink_name):
        # file name like assets/drinks/lemonade.png
        filename = drink_name.lower().replace(" ", "_")
        img = Image.open(f"./assets/drinks/{filename}.png").convert("RGBA")
        img.thumbnail((200, 200))   # keeps aspect ratio

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
        save_order(self.current_order, success)
        self.orders.append({"drink": self.current_order,"success": success})

        # Update balance
        self.current_balance = update_balance(self.current_balance,success)
        self.balance.config(text=f"BALANCE: ${self.current_balance}")

        # Show result
        if success:
            result_text = "✓ CORRECT ORDER! +$10"
            result_color = colors["green"]
            self.show_drink(self.current_order)
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

        # Clear previous result
        self.result_label.config(text="")
        self.clear_drink()
        print("Next order:", self.current_order)

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

        # Close button
        tk.Button(
            popup,
            text="OK",
            font=("retro_font", 12, "bold"),
            bg=colors["coral"],
            fg="white",
            command=popup.destroy
        ).pack(pady=20)

        print("End of day!")
        print("Rent: $30")
        print("Final balance:", self.current_balance)


    def show_menu_book(self):
        menu_window = tk.Toplevel(self)

        menu_window.title("Recipe Book")
        menu_window.configure(bg=colors["brown"])

        # Keep recipe book above the game
        menu_window.transient(self)
        menu_window.grab_set()

        # Recipe book size
        book_width = 1000
        book_height = 667

        # Load recipe book image
        book = Image.open("assets/recipe_book.png")
        book = book.resize((book_width, book_height))
        self.recipe_book_img = ImageTk.PhotoImage(book)

        # Canvas for image + recipe text
        canvas = tk.Canvas(
            menu_window,
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

        # Split recipes between the two pages
        recipe_items = list(recipes.items())

        left_recipes = recipe_items[:5]
        right_recipes = recipe_items[5:10]

        # Y positions of the five recipe boxes
        y_positions = [220, 340, 465, 590, 715]

        # Because the image is resized from 1536x1024 to 1000x667
        scale_x = book_width / 1536
        scale_y = book_height / 1024

        # Convert original image coordinates to displayed coordinates
        y_positions = [
            int(y * scale_y)
            for y in [220, 340, 465, 590, 725]
        ]

        # Recipe text function
        def draw_recipe(recipe_list, x):
            for i, (drink, ingredients) in enumerate(recipe_list):

                y = y_positions[i]

                # Drink name
                canvas.create_text(
                    x,
                    y,
                    text=drink,
                    anchor="w",
                    fill=colors["brown"],
                    font=("retro_font", 13, "bold")
                )

                # Ingredients
                ingredient_text = " + ".join(
                    ingredient.title()
                    for ingredient in ingredients
                )

                canvas.create_text(
                    x,
                    y + 24,
                    text=ingredient_text,
                    anchor="w",
                    fill=colors["muted"],
                    font=("retro_font", 10)
                )

        # Draw left page recipes
        draw_recipe(
            left_recipes,
            int(395 * scale_x)
        )

        # Draw right page recipes
        draw_recipe(
            right_recipes,
            int(875 * scale_x)
        )

        # Close button
        close_button = tk.Button(
            menu_window,
            text="CLOSE",
            font=("retro_font", 12, "bold"),
            bg=colors["coral"],
            fg="white",
            padx=25,
            pady=7,
            command=menu_window.destroy)
        close_button.pack(pady=10)

    def draw_intro():
        pass

    def show_result():
        pass

c = CashOrCrashApp()
c.intro()
c.mainloop()