import pygame
import random

from global_data import *


class Joueur:
    """
    Le joueur a à chaque instant une couleur, une case (de la classe Case),une direction
    (0,1,2,3 correspondant à la meme chose que dans Case),
    et un running pour signaler s'il faut stopper le jeu
    """
    def __init__(self,labyrinthe,case,color,direction,speed,reflection="humain"):
        self._case = case # Case actuelle. Attribut privé car son indice sera inconnue par le joueur durant la partie
        self._color = color
        self._direction = direction # Doit être initialisé à une direction valide
        self._running = True
        self.speed = speed
        self.labyrinthe = labyrinthe
        self.visu_actuel = set() # ensemble des indices de cases visibles actuellement
        self.cases_vues = set() # ensemble des indices de cases déjà vues
        self.reflexion = reflection # "humain" ou le mode de reflexion de l'IA ("aléatoire","profondeur","explorateur")
        if(self.reflexion == "explorateur"):
            self.taux_exploration_cases = {}# dictionnaire qui quantifie le taux d'exploration de chaque case
    def changement_direction(self,key,touches=None) -> None:
        """
        Met à jour la direction uniquement lors d'un nouvel appui sur une touche.
        La direction est conservée même si la touche est relâchée.
        """
        if key == pygame.K_RIGHT:
            self._direction=0
        if key == pygame.K_UP:
            self._direction=1
        if key == pygame.K_LEFT:
            self._direction =2
        if key == pygame.K_DOWN:
            self._direction=3
        if touches!=None:
            for i in range(4):
                if key == touches[i]:
                    self._direction=i            

    def get_case_absolue(self):
        """renvoie l'indice de la case"""
        return self._case.i
                   
    def deplacement(self):
        """
        Dans le cas où le joueur a cliqué sur une flèche du clavier, 
        on change la case sur laquelle il est selon la direction qu'il prend
        en vérifiant d'abord si cette case est accessible
        """
        #print("deplacement dans la direction ",self._direction)
        if self._direction == 4:# non oriente
            return
        if self._case.voisins[self._direction]:# si on peut passer
            match self._direction:
                case 0:
                    self._case = self.labyrinthe.cases[self._case.i+1]
                case 1:
                    self._case = self.labyrinthe.cases[self._case.i-self.labyrinthe.largeur]
                case 2:
                    self._case = self.labyrinthe.cases[self._case.i-1]
                case 3:
                    self._case = self.labyrinthe.cases[self._case.i+self.labyrinthe.largeur]
            if self.reflexion == "explorateur":
                if self._case.i not in self.taux_exploration_cases:
                    self.taux_exploration_cases[self._case.i] = 0
                self.taux_exploration_cases[self._case.i] += 1
                 
    def voir(self):
        """Maj le visu_actuel et les cases_vues"""
        self.visu_actuel = set()
        self.visu_actuel.add(self.get_case_absolue())
        for direction in ["haut","bas","gauche","droite"]:
            self.visu_actuel = self.visu_actuel.union(self.labyrinthe.cases[self.get_case_absolue()].visibles[direction])
            self.cases_vues = self.cases_vues.union(self.visu_actuel)
    
    def choisir_case(self)->int:
        """Choisit un indice de case parmi les cases voisines en fonction de la réflexion choisie"""
        if self.reflexion == "aléatoire":
            voisins_accessibles = []
            for i in range(4):
                if self._case.voisins[i]:
                    voisins_accessibles.append(i)
            if len(voisins_accessibles)>0:
                return random.choice(voisins_accessibles)
        elif self.reflexion == "explorateur":
            voisins_accessibles = []
            taux_exploration_voisins = []
            for i in range(4):
                if self._case.voisins[i]:
                    voisins_accessibles.append(i)
                    case_voisine = None
                    match i:
                        case 0:
                            case_voisine = self.labyrinthe.cases[self._case.i+1]
                        case 1:
                            case_voisine = self.labyrinthe.cases[self._case.i - self.labyrinthe.largeur]
                        case 2:
                            case_voisine = self.labyrinthe.cases[self._case.i-1]
                        case 3:
                            case_voisine = self.labyrinthe.cases[self._case.i + self.labyrinthe.largeur]
                    if case_voisine.i in self.taux_exploration_cases:
                        taux_exploration_voisins.append(self.taux_exploration_cases[case_voisine.i])
                    else:
                        taux_exploration_voisins.append(0)
            if len(voisins_accessibles)>0:
                min_taux = min(taux_exploration_voisins)
                meilleurs_voisins = [voisins_accessibles[i] for i in range(len(voisins_accessibles)) if taux_exploration_voisins[i]==min_taux]
                return random.choice(meilleurs_voisins)
            return random.choice(voisins_accessibles)
        return 4