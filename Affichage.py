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
    # taille_laby est la taille en pixels du labyrinthe affiché
    for case in labyrinthe.cases:
        taille_case = taille_laby/labyrinthe.largeur
        x_centre_case = (case.i % labyrinthe.largeur + 0.5) * taille_case
        y_centre_case = (case.i // labyrinthe.largeur + 0.5) * taille_case
        dessine_case_absolue(case,x_centre_case,y_centre_case,taille_case,fond,coul_mur)
    
def dessine_case_absolue(case,x_centre,y_centre,taille_case,fond,coul_mur=(0,0,0)):
    for i in range(len(case.voisins)):
        # affiche une ligne orthogonale entre les deux cases s'ils ne sont pas voisins
        # rien sinon
        #if(case.i==10):
            #print("debug case 10. x_centre=",x_centre," y_centre=",y_centre)
            #print("taille_case=",taille_case)
        if not case.voisins[i]:
            pygame.draw.line(fond,coul_mur,
                             [x_centre+math.cos((-i/4-1/8)*2*math.pi)*taille_case/2,
                              y_centre+math.sin((-i/4-1/8)*2*math.pi)*taille_case/2],
                             [x_centre+math.cos((-i/4+1/8)*2*math.pi)*taille_case/2,
                              y_centre+math.sin((-i/4+1/8)*2*math.pi)*taille_case/2],3)
    police_nationale = pygame.font.SysFont('Corbel',5) 
    text = police_nationale.render(str(case.i) , True , (0,0,0))

def affiche_joueur(fond,joueur,taille_laby):
    #utilise pygame pour afficher le joueur
    taille_case = taille_laby/joueur.labyrinthe.largeur
    x_centre_case = (joueur.get_case_absolue() % joueur.labyrinthe.largeur + 0.5) * taille_case
    y_centre_case = (joueur.get_case_absolue() // joueur.labyrinthe.largeur + 0.5) * taille_case
    pygame.draw.circle(fond,joueur._color,(x_centre_case,y_centre_case),taille_case/4)

def affiche_ensemble_de_cases(fond,labyrinthe,ensemble_cases,taille_laby,coul_mur=(0,0,0)):
    #utilise pygame pour afficher un ensemble de cases
    # ensemble_cases est un ensemble d'indices de cases
    for indice in ensemble_cases:
        case = labyrinthe.cases[indice]
        taille_case = taille_laby/labyrinthe.largeur
        x_centre_case = (case.i % labyrinthe.largeur + 0.5) * taille_case
        y_centre_case = (case.i // labyrinthe.largeur + 0.5) * taille_case
        dessine_case_absolue(case,x_centre_case,y_centre_case,taille_case,fond,coul_mur)