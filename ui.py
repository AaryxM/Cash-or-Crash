import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

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
        self.configure(bg = colors["cream"])

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
            font = ("retro_font", 12, "bold"),
            foreground = "white",
            background = colors["coral"],
            padding = (100,30),
        )
        style.map(
            "Coral.TButton",
            foreground=[("active", colors["paper"])],
            background=[("active", colors["coral_dark"])]
        )

    def clear_windows(self):
        for small_window in self.winfo_children():
            small_window.destroy()

    #Intro interface
    def intro(self):
        # displays the intro screen with game title, description, and name entry.

        self.clear_windows()
        #C = Canvas(root, height, width, bd, bg, ..)
        # canvas = tk.Canvas(self, bg = colors["sky"], bd = 0)

        #🏖️bg image
        self.config_styles()
        bgimg = Image.open("bg_img2.png")
        bgimg = bgimg.resize((1800, 915))   # new size

        self.bg_img2 = ImageTk.PhotoImage(bgimg)

        background_label = tk.Label(self, image = self.bg_img2)

        background_label.place(relwidth=1, relheight=1)

        #game logo ⚒️🛠️
        #og = 1432 × 736 
       

        logoimg = Image.open("game_logo.png")
        logoimg = logoimg.resize((700,350))

        self.logo_img = ImageTk.PhotoImage(logoimg)

        logo_label = tk.Label(self, image = self.logo_img)

        logo_label.pack()

        # start_btn = ttk.Button(self, text = "START", height="5", width="50", padx="1", pady="1", style = "Coral.TButton")
        start_btn = ttk.Button(
            self,
            text="START",
            style="Coral.TButton",
            command=self.show_game
        )
        start_btn.pack(anchor='s')

        # start_btn.bind("<Button-1>", self.show_game)

    def show_game(self):
        self.clear_windows()
        #headers with the current session details!
        header = tk.Frame(self, bg = colors["paper"], padx = 35, pady = 30)

        header.pack(side="top", fill ='both')

        tk.Label(
            header,
            text = "Cash or Crash",
            background= colors["paper"],
            foreground=colors["coral"],
            font = ("retro_font", 18, "bold"),
        ).pack(side="left")

        #🛠️⚒️connect to db for current session's balance.
        bal = 100
        self.balance = tk.Label(
            header,
            text= f"BALANCE: ${bal}",
            background=colors["paper"],
            foreground=colors["brown"],
            font = ("retro_font", 18, "bold"),
            justify = "left"
        )

        self.balance.pack(side="right")
        #1048 x 517
        _stand = Image.open("stand_img.png")
        _stand = _stand.resize((1700, 900))

        self.stand_img = ImageTk.PhotoImage(_stand)

        stand_label = tk.Label(self, image = self.stand_img, background=colors["sky"])

        stand_label.pack(side="top")



    def draw_intro():
        pass


    def show_result():
        pass

c = CashOrCrashApp()
c.intro()
c.mainloop()
