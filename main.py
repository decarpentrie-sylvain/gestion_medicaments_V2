import tkinter as tk
from interfaces.interface_main_gui import Application

if __name__ == "__main__":
    root = tk.Tk()
    app = Application(root)
    app.pack(fill="both", expand=True)
    root.mainloop()