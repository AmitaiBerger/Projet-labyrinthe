import random



class Case():
    #voisins = [None,None,None,None]
    #contenu = None

    def __init__(self,indice=0):
        self.voisins = [None,None,None,None]# booléens contenant True si la case et conectée à la voisine
        # l'indice 0 est la droite, 1 le haut, 2 la gauche et 3 le bas.
        self.contenu = None# pour l'instant inutile, mais poura contenir des éléments graphiques cosmétiques
        self.i = indice
    


class Labyrinthe():

    def __init__(self,hauteur:int,largeur:int):
        self.cases = []
        self.largeur=largeur
        self.hauteur=hauteur
    
    def directions_voisines(self,indice_centre:int):
        """renvoie la liste directions possibles à partir d'une case donnée
        sous forme d'un entier (une direction impossible est un coté extérieur du labyrinthe)
           droite : 0
           haut : 1
           gauche : 2
           bas : 3
           """

        print("directions voisins à ", indice_centre)
        directions = [] #
        if not (indice_centre%self.largeur==0):# (pas à gauche)
            directions.append(2)
        if not (indice_centre%self.largeur==self.largeur-1):# pas à droite
            directions.append(0)
        if not (indice_centre//self.largeur==0): # pas en haut
            directions.append(1)
        if not (indice_centre//self.largeur==self.hauteur-1):# on n'est pas en bas
            directions.append(3)
        return directions

    def indices_voisins(self,indice_centre:int):
        print("indices voisins à ", indice_centre)
        vois = []
        if not (indice_centre%self.largeur<=0):# (pas à gauche)
            vois.append(indice_centre-1)
        if not (indice_centre%self.largeur>=self.largeur-1):
            vois.append(indice_centre+1)
        if not (indice_centre//self.largeur<=0): # pas en haut
            vois.append(indice_centre-self.largeur)
        if not (indice_centre//self.largeur>=self.hauteur-1):# on n'est pas en bas
            vois.append(indice_centre+self.largeur)
        return vois
    
    def generer_par_Wilson(self):
        """crée un labyrinthe avec l'algorithme de Wilson.
        documentaiton en anglais :
        https://en.wikipedia.org/wiki/Maze_generation_algorithm#Wilson's_algorithm
        """
        print("generation par Wilson")
        cases_non_generees = [i for i in range(self.largeur*self.hauteur)]# indice des cases pas encore partie du Laby
        self.cases.append(Case(random.choice(cases_non_generees)))# on prend un point au hasard pour appartenir au Laby
        print("premiere case du Labyrinthe :",self.cases[0])
        cases_non_generees.remove(self.cases[0].i)
        print("premiere case du Laby :",self.cases[0])
        while(len(self.cases)<self.hauteur*self.largeur):
            print("génération d'une branche")
            # génération de la premiere case de la branche
            caseActu = random.choice(cases_non_generees)
            
            print("à partir de :",caseActu)
            cheminActu = [caseActu]
            while caseActu in cases_non_generees:
                voisins = self.indices_voisins(caseActu)
                prochain = random.choice(voisins)
                if(prochain in cheminActu):# si on fait une boucle, on supprime
                    cheminActu = cheminActu[:cheminActu.index(prochain)+1]
                else:
                    cheminActu.append(prochain)
                caseActu = prochain

            # on a trouvé un chemin qui rejoint le labyrinthe
            print("chemin trouvé :",cheminActu)

            # On ajoute le chemin au labyrinthe
            for i in range(len(cheminActu)-1):
                if not any(c.i == cheminActu[i] for c in self.cases):
                    self.cases.append(Case(cheminActu[i]))
                    self.cases[-1].voisins.append(cheminActu[i+1])
                    if(i>0):
                        self.cases[-1].voisins.append(cheminActu[i-1])
            self.cases.append(Case(cheminActu[-1]))
            self.cases[-1].voisins.append(cheminActu[-2])

            # enlever les cases de cases_non_generees :
            for case in cheminActu:
                if case in cases_non_generees:
                    cases_non_generees.remove(case)
            
                
        print("labyrinthe généré")
            #connecte = not(self.indices_voisins(caseActu).issubset(cases_non_generees))




