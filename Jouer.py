
def class Joueur:
    """
    Le joueur a à chaque instant une couleur, une case et une 
    direction qui peut etre droite gauche haut bas ou rien
    (qui correspondront à des constantes de pygame)
    """
    def__init__(self,case,color,direction,vision):
        self._case=case
        self._color=color
        self._direction=direction
        self._vision=vision
        
    def deplacement(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key==K_DOWN
                    direction
                    
                    
