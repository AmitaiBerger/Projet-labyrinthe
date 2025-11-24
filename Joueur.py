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
        self._case = case
        self._color = color
        self._direction = direction # Doit être initialisé à une direction valide
        self._running = True
        self.speed = speed
        self.labyrinthe = labyrinthe
        
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
                match event.key:
                    case pygame.K_RIGHT:
                        self._direction = 0
                    case pygame.K_UP:
                        self._direction = 1
                    case pygame.K_LEFT:
                        self._direction = 2
                    case pygame.K_DOWN:
                        self._direction = 3
                    # Si une autre touche est pressée, on ne fait rien, 
                    # on garde l'ancienne direction.

                
                    
    def deplacement(self)->None:
        """
        Dans le cas où le joueur a cliqué sur une flèche du clavier, 
        on change la case sur laquelle il est selon la direction qu'il prend
        en vérifiant d'abord si cette case est accessible
        """
        if self.direction == 4:
            return None
        if self.case[self.direction]:
            match direction:
                case 0:
                    self._case = labyrinthe.cases[self._case.i+1]
                case 1:
                    self._case = labyrinthe.cases[self._case.i-labyrinthe.largeur]
                case 2:
                    self._case = labyrinthe.cases[self._case.i-1]
                case 3:
                    self._case = labyrinthe.cases[self._case.i+labyrinthe.largeur]

                    
