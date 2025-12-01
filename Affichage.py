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

def affiche_labyrinthe(fond,labyrinthe,taille_laby,coul_mur=(0,0,0)):
    #utilise pygame pour afficher le labyrinthe
    for case in labyrinthe.cases:
        for voisin in case.voisins:
            # affiche une ligne orthogonale entre les deux cases s'ils ne sont pas voisins
            # rien sinon
            taille_case = taille_laby/labyrinthe.cases
            pygame.draw.line(fond,coul_mur,taille_laby/labyrinthe.largeur)
            pass
