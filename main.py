import tkinter as tk
from ui import IntroFrame, MenuFrame, GameFrame
# from db import init_db   
# uncomment later when you add SQL

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cash or Crash: Juice Stand")
        self.geometry("800x600")

        # Initialize DB later
        # init_db()

        # Container for frames
        self.frames = {}
        for F in (IntroFrame, MenuFrame, GameFrame):
            frame = F(self, self.switch_frame)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Start with Intro
        self.switch_frame("IntroFrame")

    def switch_frame(self, frame_name):
        """Raise the selected frame to the top."""
        self.frames[frame_name].tkraise()

if __name__ == "__main__":
    app = App()
    app.mainloop()
