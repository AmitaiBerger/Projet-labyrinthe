import tkinter as tk
from tkinter import messagebox
import pygame

class Fenetre:
    def __init__(self):
        root = tk.Tk()
        root.title("MAIN")

        fen = tk.Toplevel(root)
        fen.title("Hello")
        fen.but1 = tk.Button(fen,
            text="click",
            command= lambda : messagebox.showinfo("..",
                "!")
            )
        fen.but1.pack()

        root.mainloop()
