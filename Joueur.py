import pygame
import global


class Joueur:
    """
    Le joueur a à chaque instant une couleur, une case (de la classe Case),une direction
    (0,1,2,3 correspondant à la meme chose que dans Case, ou 4 pour la direction nulle),
    et un running pour signaler s'il faut stopper le jeu
    """
    def __init__(self,labyrinthe,case,color,direction,running):
        self._case = case
        self._color = color
        self._direction = direction
        self._running = True
        
    def changement_direction(self)->None:
        """
        On détecte les cases pressées, si deux cases sont pressées à la fois 
        """
        keys = pygame.key.get_pressed()
        if pygame.event.get()[0].type == pygame.QUIT:
            self._running = False
        elif not any(keys) or len(pygame.event.get())>1:
                self._direction = 4
        elif pygame.event.type == pygame.KEYDOWN:
            match pygame.event.key:
                case K_RIGHT:
                    self._direction = EST
                case K_UP:
                    self._direction = NORD
                case K_LEFT:
                    self._direction = OUEST
                case K_DOWN:
                    self._direction = SUD
                case _:
                    self.direction = 4

                
                    
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

                    
