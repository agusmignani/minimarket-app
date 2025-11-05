# Archivo principal (incia la app)

#main.py
import tkinter as tk
from modules.login import LoginApp

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()
