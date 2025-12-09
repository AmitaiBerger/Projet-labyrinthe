import pygame

from global_data import *


class Joueur:
    """
    Le joueur a à chaque instant une couleur, une case (de la classe Case),une direction
    (0,1,2,3 correspondant à la meme chose que dans Case),
    et un running pour signaler s'il faut stopper le jeu
    """
    def __init__(self,labyrinthe,case,color,direction,speed):
        self._case = case # Case actuelle. Attribut privé car son indice sera inconnue par le joueur durant la partie
        self._color = color
        self._direction = direction # Doit être initialisé à une direction valide
        self._running = True
        self.speed = speed
        self.labyrinthe = labyrinthe
        self.visu_actuel = set() # ensemble des indices de cases visibles actuellement
        self.cases_vues = set() # ensemble des indices de cases déjà vues
        
    def changement_direction(self,key) -> None:
        """
        Met à jour la direction uniquement lors d'un nouvel appui sur une touche.
        La direction est conservée même si la touche est relâchée.
        """
        if key == pygame.K_RIGHT:
            self.direction=0
        if key == pygame.K_UP:
            self.direction=1
        if key == pygame.K_LEFT:
            self.direction =2
        if key == pygame.K_DOWN:
            self.direction=3


                

    def get_case_absolue(self):
        return self._case.i


                    
    def deplacement(self):
        """
        Dans le cas où le joueur a cliqué sur une flèche du clavier, 
        on change la case sur laquelle il est selon la direction qu'il prend
        en vérifiant d'abord si cette case est accessible
        """
        if self.direction == 4:# non oriente
            return
        if self._case.voisins[self.direction]:# si on peut passer
            match self.direction:
                case 0:
                    self._case = self.labyrinthe.cases[self._case.i+1]
                case 1:
                    self._case = self.labyrinthe.cases[self._case.i-self.labyrinthe.largeur]
                case 2:
                    self._case = self.labyrinthe.cases[self._case.i-1]
                case 3:
                    self._case = self.labyrinthe.cases[self._case.i+self.labyrinthe.largeur]

                    
    def voir(self):
        """Maj le visu_actuel et les cases_vues"""
        self.visu_actuel = set()
        self.visu_actuel.add(self.get_case_absolue())
        for direction in ["haut","bas","gauche","droite"]:
            self.visu_actuel = self.visu_actuel.union(self.labyrinthe.cases[self.get_case_absolue()].visibles[direction])
            self.cases_vues = self.cases_vues.union(self.visu_actuel)