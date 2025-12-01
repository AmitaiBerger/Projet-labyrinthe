import pygame
from pygame.locals import K_RIGHT, K_UP, K_LEFT, K_DOWN

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
        self.touches_direction = [pygame.K_z, pygame.K_q, pygame.K_s, pygame.K_d]
        self.visu_actuel = set() # ensemble des indices de cases visibles actuellement
        self.cases_vues = set() # ensemble des indices de cases déjà vues
        
    def changement_direction(self) -> None:
        """
        Met à jour la direction uniquement lors d'un nouvel appui sur une touche.
        La direction est conservée même si la touche est relâchée.
        """
        for event in pygame.event.get():
            # 1. Gestion de la fermeture
            if event.type == pygame.QUIT:
                self._running = False
                return

            # 2. Changement de direction (seulement si une touche est ENFONCÉE)
            if event.type == pygame.KEYDOWN:
                self.tourner_suivant_key(event.key)
                

    def get_case_absolue(self):
        return self._case.i

    def tourner_suivant_key_ou_deplacer(self,key) -> None:
        for i in range(4):
            if(self.touches_direction[i] == key):
                if(self._direction == i):
                    self.deplacement()
                else:
                    self._direction = i
                return None
        
                    
    def deplacement(self)->None:
        """
        Dans le cas où le joueur a cliqué sur une flèche du clavier, 
        on change la case sur laquelle il est selon la direction qu'il prend
        en vérifiant d'abord si cette case est accessible
        """
        if self.direction == 4:# non oriente
            return None
        if self.case.voisins[self.direction]:# si on peut passer
            match self.direction:
                case 0:
                    self._case = self.labyrinthe.cases[self._case.i+1]
                case 1:
                    self._case = self.labyrinthe.cases[self._case.i-self.labyrinthe.largeur]
                case 2:
                    self._case = self.labyrinthe.cases[self._case.i-1]
                case 3:
                    self._case = self.labyrinthe.cases[self._case.i+self.labyrinthe.largeur]

                    
