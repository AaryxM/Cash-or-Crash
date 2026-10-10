
from db import init_db
from ui import CashOrCrashApp


if __name__ == "__main__":
    init_db()

    app = CashOrCrashApp()
    app.title("Cash or Crash: Juice Stand")
    app.login_screen()
    app.mainloop()

