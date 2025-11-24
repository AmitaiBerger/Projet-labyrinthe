import random



class Case():
    #voisins = [None,None,None,None]
    #contenu = None

    def __init__(self,indice=0):
        self.voisins = [None,None,None,None]# booléens contenant True si la case et conectée à la voisine
        # l'indice 0 est la droite, 1 le haut, 2 la gauche et 3 le bas.
        self.contenu = None# pour l'instant inutile, mais poura contenir des éléments graphiques cosmétiques
        self.i = indice
        self.visibles = {} #Liste des cases visibles c a d les cases sans murs alignees


    


class Labyrinthe():

    def __init__(self,hauteur:int,largeur:int):
        self.cases = [Case(i) for i in range(largeur * hauteur)]
        self.largeur=largeur
        self.hauteur=hauteur

    def trier_cases(self):
        """Trie le tableau self.cases selon l'attribut i de chaque case
        pour que self.cases[k].i == k"""
        self.cases.sort(key=lambda case: case.i)

    def afficher_comme_texte(self):# généré par IA parce que peu intéressant et laborieux
        """affiche le labyrinthe sous forme de texte dans la console
        utile pour le debug"""
        print("affichage du labyrinthe")
        for h in range(self.hauteur):
            # ligne du haut
            ligne_haut = ""
            for l in range(self.largeur):
                ligne_haut += "+"
                if self.cases[h*self.largeur+l].voisins[1] != None:
                    ligne_haut += "   "
                else:
                    ligne_haut += "---"
            ligne_haut += "+"
            print(ligne_haut)

            # ligne du milieu
            ligne_milieu = ""
            for l in range(self.largeur):
                if self.cases[h*self.largeur+l].voisins[2] != None:
                    ligne_milieu += " "
                else:
                    ligne_milieu += "|"
                ligne_milieu += "   "
            if self.cases[h*self.largeur+self.largeur-1].voisins[0] != None:
                ligne_milieu += " "
            else:
                ligne_milieu += "|"
            print(ligne_milieu)
        # ligne du bas
        ligne_bas = ""
        for l in range(self.largeur):
            ligne_bas += "+"
            if self.cases[(self.hauteur-1)*self.largeur+l].voisins[3] != None:
                ligne_bas += "   "
            else:
                ligne_bas += "---"
        ligne_bas += "+"
        print(ligne_bas)

    
    def directions_voisines(self,indice_centre:int):
        """renvoie la liste directions possibles à partir d'une case donnée
        sous forme d'un entier (une direction impossible est un coté extérieur du labyrinthe)
           droite : 0
           haut : 1
           gauche : 2
           bas : 3
           """

        #print("directions voisins à ", indice_centre)
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

    def connecter_cases(self, indiceA, indiceB):
        """Connecte deux cases adjacentes dans les deux sens"""
        dir_A_vers_B = self.direction(indiceA, indiceB)
        dir_B_vers_A = (dir_A_vers_B + 2) % 4
        
        self.cases[indiceA].voisins[dir_A_vers_B] = True
        self.cases[indiceB].voisins[dir_B_vers_A] = True

    def indices_voisins(self,indice_centre:int):
        #print("indices voisins à ", indice_centre)
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
    
    def direction(self,indiceA,indiceB):# généré par IA, utile pour la fonction Wilson
        """renvoie la direction de B par rapport à A
           droite : 0
           haut : 1
           gauche : 2
           bas : 3
           """
        if indiceB == indiceA+1:
            return 0
        elif indiceB == indiceA-1:
            return 2
        elif indiceB == indiceA-self.largeur:
            return 1
        elif indiceB == indiceA+self.largeur:
            return 3
        else:
            return None


    def generer_par_Wilson(self):
        """crée un labyrinthe avec l'algorithme de Wilson.
        documentaiton en anglais :
        https://en.wikipedia.org/wiki/Maze_generation_algorithm#Wilson's_algorithm
        """
        print("generation par Wilson")
        
        cases_dans_laby = set()
        premiere = random.randrange(self.largeur * self.hauteur)
        cases_dans_laby.add(premiere)
        #print("premiere case du Labyrinthe :", premiere)
        cases_non_generees = set(range(self.largeur * self.hauteur)) - cases_dans_laby
        while(cases_non_generees):
            #print("génération d'une branche")
            # génération de la premiere case de la branche
            caseActu = random.choice(list(cases_non_generees))
            
            #print("à partir de :",caseActu)
            cheminActu = [caseActu]
            while caseActu not in cases_dans_laby:
                voisins = self.indices_voisins(caseActu)
                prochain = random.choice(voisins)
                #print("prochain :",prochain)
                if(prochain in cheminActu):# si on fait une boucle, on supprime
                    #print("boucle")
                    cheminActu = cheminActu[:cheminActu.index(prochain)+1]
                else:
                    cheminActu.append(prochain)
                caseActu = prochain

            # on a trouvé un chemin qui rejoint le labyrinthe
            #print("chemin trouvé :",cheminActu)

            # On ajoute le chemin au labyrinthe
            for i in range(len(cheminActu)-1):
                #if not any(c.i == cheminActu[i] for c in self.cases):
                self.connecter_cases(cheminActu[i], cheminActu[i + 1])
                cases_dans_laby.add(cheminActu[i])
                cases_non_generees.discard(cheminActu[i])
            #self.cases.append(Case(cheminActu[-1]))
            #self.cases[-1].voisins[dir] = True

        
        print("labyrinthe généré")

    def visibles(self):
        for case in self.cases:
            vision = {}
            vision["droite"] = []
            vision["haut"] = []
            vision["gauche"] = []
            vision["bas"] = []
            position = case.i
            while self.cases[position].voisins[0] == True:
                position += 1
                vision["droite"].append(position)
            position = case.i
            while self.cases[position].voisins[1] == True:
                position -= self.largeur
                vision["haut"].append(position)
            position = case.i
            while self.cases[position].voisins[2] == True:
                position -= 1
                vision["gauche"].append(position)
            position = case.i
            while self.cases[position].voisins[3] == True:
                position += self.largeur
                vision["bas"].append(position)
            case.visibles = vision
    
            





