import tkinter as tk
from tkinter import messagebox
import pygame
import math
import Joueur
from dataclasses import dataclass

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

@dataclass
class Camera:
    """informations d'affichage"""
    centrage = "absolu" #ou centré sur un élément/joueur auquel cas contient l'objet cible
    hauteur_vision = 0# nb cases 
    largeur_vision = 0# nb cases
    


def affiche_labyrinthe(fond,labyrinthe,taille_laby,type_vision="absolue",coul_mur=(0,0,0)):
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
                             [x_centre+math.cos((-i/4-1/8)*2*math.pi)*taille_case*math.sqrt(2)/2,
                              y_centre+math.sin((-i/4-1/8)*2*math.pi)*taille_case*math.sqrt(2)/2],
                             [x_centre+math.cos((-i/4+1/8)*2*math.pi)*taille_case*math.sqrt(2)/2,
                              y_centre+math.sin((-i/4+1/8)*2*math.pi)*taille_case*math.sqrt(2)/2],3)
    police_nationale = pygame.font.SysFont('Corbel',5) 
    text = police_nationale.render(str(case.i) , True , (0,0,0))

def afficher_joueur(fond,joueur,taille_laby,Camera=None):
    #utilise pygame pour afficher le joueur
    if Camera==None or Camera.centrage=="absolu":
        taille_case = taille_laby/joueur.labyrinthe.largeur
        x_centre_case = (joueur.get_case_absolue() % joueur.labyrinthe.largeur + 0.5) * taille_case
        y_centre_case = (joueur.get_case_absolue() // joueur.labyrinthe.largeur + 0.5) * taille_case
        pygame.draw.circle(fond,joueur._color,(x_centre_case,y_centre_case),taille_case/4)
    elif type(Camera.centrage)==Joueur:
        taille_case = taille_laby/joueur.labyrinthe.largeur
        pygame.draw.circle(fond,joueur._color,(taille_laby/2,taille_laby/2),taille_case/4)
    else:
        raise ValueError("type de centrage inconnu pour l'affichage du joueur")

def effacer_joueur(fond,joueur,taille_laby,Camera=None):
    if Camera==None or Camera.centrage=="absolu":
        taille_case = taille_laby/joueur.labyrinthe.largeur
        x_centre_case = (joueur.get_case_absolue() % joueur.labyrinthe.largeur + 0.5) * taille_case
        y_centre_case = (joueur.get_case_absolue() // joueur.labyrinthe.largeur + 0.5) * taille_case
        pygame.draw.circle(fond,(255, 255, 255),(x_centre_case,y_centre_case),taille_case/4)
    elif type(Camera.centrage)==Joueur:
        taille_case = taille_laby/joueur.labyrinthe.largeur
        pygame.draw.circle(fond,(255, 255, 255),(taille_laby/2,taille_laby/2),taille_case/4)
    else:
        raise ValueError("type de centrage inconnu pour l'effacement du joueur")
def affiche_ensemble_de_cases(fond,labyrinthe,ensemble_cases,taille_laby,coul_mur=(0,0,0),directionnel=False,Camera=None):
    """utilise pygame pour afficher un ensemble de cases
    ensemble_cases est un ensemble d'indices de cases
    relatif_a permet de définir un affichage centré autour d'une case
    taille_lay : taille en pixels du labyrinthe affiché"""
    if not directionnel:
        if Camera == None or Camera.centrage == "absolu":
            for indice in ensemble_cases:
                case = labyrinthe.cases[indice]
                taille_case = taille_laby/labyrinthe.largeur
                x_centre_case = (case.i % labyrinthe.largeur + 0.5) * taille_case
                y_centre_case = (case.i // labyrinthe.largeur + 0.5) * taille_case
                dessine_case_absolue(case,x_centre_case,y_centre_case,taille_case,fond,coul_mur)
        else:
            for indice in ensemble_cases:
                case = labyrinthe.cases[indice]
                taille_case = taille_laby/Camera.largeur_vision
                Case_centre = Camera.centrage.get_case_absolue()
                
                x_centre_case = (case.i % labyrinthe.largeur - Case_centre.i % labyrinthe.largeur# le centre en haut à gauche
                                  + Camera.largeur_vision/2 + 0.5) * taille_case#le centre au centre
                y_centre_case = (case.i // labyrinthe.largeur - Case_centre.i // labyrinthe.largeur
                                  + Camera.hauteur_vision/2 + 0.5) * taille_case
                dessine_case_absolue(case,x_centre_case,y_centre_case,taille_case,fond,coul_mur)
    else:       
        raise NotImplementedError("affichage directionnel non implémenté pour l'instant")