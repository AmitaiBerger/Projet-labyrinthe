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
    centrage : str = "absolu" #ou centré sur un élément/joueur auquel cas contient l'objet cible
    hauteur_vision : int=0# nb cases 
    largeur_vision : int=0# nb cases total de gauche à droite
    


def affiche_labyrinthe(fond,labyrinthe,taille_laby,coul_mur=(0,0,0)):
    #utilise pygame pour afficher le labyrinthe
    # taille_laby est la taille en pixels du labyrinthe affiché
    for case in labyrinthe.cases:
        taille_case = taille_laby/labyrinthe.largeur
        x_centre_case = (case.i % labyrinthe.largeur + 0.5) * taille_case
        y_centre_case = (case.i // labyrinthe.largeur + 0.5) * taille_case
        dessine_case_absolue(case,x_centre_case,y_centre_case,taille_case,fond,coul_mur)
    
def dessine_case_absolue(case,x_centre:int,y_centre:int,taille_case:int,
                            fond,coul_mur=(0,0,0),afficher_images=True):
    """Dessine une case à partir des coordonnées en pixels exactes et absolues de son centre
        afficher_images : booléen, si True affiche une image pour la sortie"""
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
    
    if(case.contenu == "Sortie"): 
        if(afficher_images):
            taille_image = int(taille_case*0.75)
            image_sortie = pygame.image.load("images/sortie.png")
            image_sortie = pygame.transform.scale(image_sortie,(taille_image,taille_image))
            fond.blit(image_sortie,(x_centre - taille_image/2, y_centre - taille_image/2))
        else:
            police_nationale = pygame.font.SysFont('Corbel',int(taille_case)//3)
            texte_sortie = police_nationale.render("#" , True , (0,0,0))
            fond.blit(texte_sortie, (x_centre - taille_case/4, y_centre - taille_case/4))
    #fenetre.blit(text, rect)

def afficher_joueur(fond,joueur,taille_laby,camera=None,coul_partic=None):
    #utilise pygame pour afficher le joueur
    if camera==None or camera.centrage=="absolu":
        taille_case = taille_laby/joueur.labyrinthe.largeur
        x_centre_case = (joueur.get_case_absolue() % joueur.labyrinthe.largeur + 0.5) * taille_case
        y_centre_case = (joueur.get_case_absolue() // joueur.labyrinthe.largeur + 0.5) * taille_case
        pygame.draw.circle(fond,(joueur._color if coul_partic==None else coul_partic),(x_centre_case,y_centre_case),taille_case/4)
    elif isinstance(camera.centrage,Joueur.Joueur):
        taille_case = taille_laby/camera.largeur_vision
        pygame.draw.circle(fond,(joueur._color if coul_partic==None else coul_partic),(taille_laby/2,taille_laby/2),taille_case/4)
    else:
        print("camera.centrage=",camera.centrage)
        raise ValueError("type de centrage inconnu pour l'affichage du joueur")

def effacer_joueur(fond,joueur,taille_laby,camera=None,couleur_fond=(255, 255,255)):
    afficher_joueur(fond,joueur,taille_laby,camera=camera,coul_partic=couleur_fond)
    """if camera==None or camera.centrage=="absolu":
        taille_case = taille_laby/joueur.labyrinthe.largeur
        x_centre_case = (joueur.get_case_absolue() % joueur.labyrinthe.largeur + 0.5) * taille_case
        y_centre_case = (joueur.get_case_absolue() // joueur.labyrinthe.largeur + 0.5) * taille_case
        pygame.draw.circle(fond,couleur_fond,(x_centre_case,y_centre_case),taille_case/4)
    elif isinstance(camera.centrage,Joueur.Joueur):
        taille_case = taille_laby/camera.largeur_vision
        pygame.draw.circle(fond,couleur_fond,(taille_laby/2,taille_laby/2),taille_case/4)
    else:
        print("camera.centrage=",camera.centrage)
        raise ValueError("type de centrage inconnu pour l'effacement du joueur")"""
def affiche_ensemble_de_cases(fond,labyrinthe,ensemble_cases,taille_laby,coul_mur=(0,0,0),directionnel=False,camera=None):
    """utilise pygame pour afficher un ensemble de cases
    ensemble_cases est un ensemble d'indices de cases
    relatif_a permet de définir un affichage centré autour d'une case
    taille_lay : taille en pixels du labyrinthe affiché"""
    if not directionnel:
        if camera == None or camera.centrage == "absolu":
            for indice in ensemble_cases:
                case = labyrinthe.cases[indice]
                taille_case = taille_laby/labyrinthe.largeur
                x_centre_case = (case.i % labyrinthe.largeur + 0.5) * taille_case
                y_centre_case = (case.i // labyrinthe.largeur + 0.5) * taille_case
                dessine_case_absolue(case,x_centre_case,y_centre_case,taille_case,fond,coul_mur)
        elif isinstance(camera.centrage,Joueur.Joueur):
            for indice in ensemble_cases:
                case = labyrinthe.cases[indice]
                taille_case = taille_laby/camera.largeur_vision
                case_centre = camera.centrage.get_case_absolue()
                
                x_centre_case = (case.i % labyrinthe.largeur - (case_centre % labyrinthe.largeur)# le centre en haut à gauche
                                  + camera.largeur_vision/2) * taille_case#le centre au centre
                y_centre_case = (case.i // labyrinthe.largeur - (case_centre // labyrinthe.largeur)
                                  + camera.hauteur_vision/2) * taille_case
                
                if(x_centre_case>=-taille_case/2 and x_centre_case<=taille_laby+taille_case/2
                   and y_centre_case>=-taille_case/2 and y_centre_case<=taille_laby+taille_case/2):
                    #print("case centre=",case_centre)
                    #print("case i=",case.i)
                    #print("x_centre =",x_centre_case/taille_case," y_centre =",y_centre_case/taille_case)
                    dessine_case_absolue(case,x_centre_case,y_centre_case,taille_case,fond,coul_mur)
        else:
            print("camera.centrage=",camera.centrage)
            raise ValueError("type de centrage inconnu pour l'affichage des cases")
    else:       
        raise NotImplementedError("affichage directionnel non implémenté pour l'instant")

def tout_effacer(fenetre,couleur_fond=(255, 255,255)):
    fenetre.fill(couleur_fond)