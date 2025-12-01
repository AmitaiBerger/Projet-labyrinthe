import tkinter as tk
from tkinter import messagebox
import pygame
import math

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
        taille_case = taille_laby/labyrinthe.cases
        x_centre_case = (case.i % labyrinthe.largeur + 0.5) * taille_case
        y_centre_case = (case.i // labyrinthe.largeur + 0.5) * taille_case
        for i in range(len(case.voisins)):
            # affiche une ligne orthogonale entre les deux cases s'ils ne sont pas voisins
            # rien sinon
            pygame.draw.line(fond,coul_mur,x_centre_case+math.cos(i*2*math.pi)*taille_case,
                             y_centre_case+math.sin((i+0.25)*2*math.pi)*taille_case,
                                x_centre_case+math.cos(i*2*math.pi)*taille_case/2,
                                y_centre_case+math.sin((i-0.25)*2*math.pi)*taille_case/2,3)
    
def affiche_joueur(fond,joueur,taille_laby):
    #utilise pygame pour afficher le joueur
    taille_case = taille_laby/joueur.labyrinthe.cases
    x_centre_case = (joueur.get_case_absolue() % joueur.labyrinthe.largeur + 0.5) * taille_case
    y_centre_case = (joueur.get_case_absolue() // joueur.labyrinthe.largeur + 0.5) * taille_case
    pygame.draw.circle(fond,joueur._color,(x_centre_case,y_centre_case),taille_case/4)

def affiche_ensemble_de_cases(fond,labyrinthe,ensemble_cases,taille_laby,coul_case=(0,0,0)):
    #utilise pygame pour afficher un ensemble de cases
    # ensemble_cases est un ensemble d'indices de cases
    for indice in ensemble_cases:
        case = labyrinthe.cases[indice]
        taille_case = taille_laby/labyrinthe.cases
        x_centre_case = (case.i % labyrinthe.largeur + 0.5) * taille_case
        y_centre_case = (case.i // labyrinthe.largeur + 0.5) * taille_case
        pygame.draw.rect(fond,coul_case,(x_centre_case-taille_case/2,
                                         y_centre_case-taille_case/2,
                                         taille_case,taille_case))