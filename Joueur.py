import pygame
import random
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
        self.cases_explorees = set() # pour le robot intelligent
        self.cases_explorees.add(self.get_case_absolue()) # pour le robot intelligent
        self.chemin_retour = [] # pour le robot intelligent
        
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
    
    def set_case_absolue(self, indice):
        """Force la position du joueur (utile pour le réseau)"""
        if 0 <= indice < len(self.labyrinthe.cases):
            self._case = self.labyrinthe.cases[indice]
                   
    def deplacement(self):
        """
        Dans le cas où le joueur a cliqué sur une flèche du clavier, 
        on change la case sur laquelle il est selon la direction qu'il prend
        en vérifiant d'abord si cette case est accessible
        """
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
                 
    def voir(self):
        """Maj le visu_actuel et les cases_vues"""
        self.visu_actuel = set()
        self.visu_actuel.add(self.get_case_absolue())
        for direction in ["haut","bas","gauche","droite"]:
            # Vérification de sécurité pour éviter les crashs si la structure visible est vide
            if direction in self.labyrinthe.cases[self.get_case_absolue()].visibles:
                self.visu_actuel = self.visu_actuel.union(self.labyrinthe.cases[self.get_case_absolue()].visibles[direction])
        self.cases_vues = self.cases_vues.union(self.visu_actuel)

    def bot_move(self, intelligent=False):
        """
        Gère le déplacement automatique.
        intelligent=False : Robot aléatoire.
        intelligent=True  : Robot explorateur (DFS / Backtracking).
        """
        # On marque l'endroit où on se trouve comme "Exploré"
        idx_actuel = self.get_case_absolue()
        self.cases_explorees.add(idx_actuel)

        # 1. Identifier les murs et passages ouverts
        directions_valides = []
        for i in range(4):
            if self._case.voisins[i]: 
                directions_valides.append(i)
        
        if not directions_valides: return 

        if not intelligent:
            # --- MODE FACILE (Aléatoire) ---
            self._direction = random.choice(directions_valides)
            self.deplacement()
            self.voir()
            return

        # --- MODE MALIN (Exploration Méthodique) ---
        
        # On cherche les voisins accessibles qu'on n'a JAMAIS visités physiquement
        candidats_inconnus = []
        for d in directions_valides:
            # Calcul de l'indice du voisin
            idx_cible = -1
            if d == 0: idx_cible = idx_actuel + 1
            elif d == 1: idx_cible = idx_actuel - self.labyrinthe.largeur
            elif d == 2: idx_cible = idx_actuel - 1
            elif d == 3: idx_cible = idx_actuel + self.labyrinthe.largeur
            
            # C'est ici que ça change : on vérifie cases_explorees, PAS cases_vues
            if idx_cible not in self.cases_explorees:
                candidats_inconnus.append(d)

        if candidats_inconnus:
            # CAS 1 : On avance vers l'inconnu
            # On note qu'on vient d'ici (pour le retour)
            self.chemin_retour.append(idx_actuel)
            
            choix = random.choice(candidats_inconnus)
            self._direction = choix
            self.deplacement()
        
        elif self.chemin_retour:
            # CAS 2 : Cul-de-sac ou zone connue -> On REBROUSSE CHEMIN
            # On récupère la dernière intersection visitée
            case_retour = self.chemin_retour.pop()
            
            # On trouve la direction pour y aller
            dir_retour = self.labyrinthe.direction(idx_actuel, case_retour)
            
            if dir_retour is not None:
                self._direction = dir_retour
                self.deplacement()
            else:
                # Sécurité (ne devrait pas arriver si le chemin est continu)
                self._direction = random.choice(directions_valides)
                self.deplacement()
        else:
            # CAS 3 : Labyrinthe entièrement exploré ou bloqué au départ
            # On bouge au hasard pour ne pas planter
            self._direction = random.choice(directions_valides)
            self.deplacement()

        # Mise à jour de la vision (pour l'affichage)
        self.voir()