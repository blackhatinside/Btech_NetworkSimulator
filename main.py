# network_simulator/main.py

import tkinter as tk
from gui.main_window import MainWindow

def main():
    root = tk.Tk()
    app = MainWindow(root)
    app.run()

if __name__ == "__main__":
    main()