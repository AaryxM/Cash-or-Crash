from ui import CashOrCrashApp

# Entry point: run  python main.py  to start the game
if __name__ == "__main__":
    app = CashOrCrashApp()
    app.title("Cash or Crash: Juice Stand")
    app.intro()
    app.mainloop()
