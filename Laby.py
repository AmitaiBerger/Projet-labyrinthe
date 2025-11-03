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
        self.cases = []
        self.largeur=largeur
        self.hauteur=hauteur

    def afficher_comme_texte(self):# généré par IA parce que peu intérressant et laborieux
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
                    #on connecte au suivant
                    dir = self.direction(cheminActu[i],cheminActu[i+1])
                    self.cases[-1].voisins[dir] = True
                    if(i>0):
                        #on connecte au précédent
                        self.cases[-1].voisins.append(cheminActu[i-1])
                        dir = self.direction(cheminActu[i],cheminActu[i-1])
                        self.cases[-1].voisins[dir] = True
            self.cases.append(Case(cheminActu[-1]))
            dir = self.direction(cheminActu[-1],cheminActu[-2])
            self.cases[-1].voisins[dir] = True

            # enlever les cases de cases_non_generees :
            for case in cheminActu:
                if case in cases_non_generees:
                    cases_non_generees.remove(case)
            
                
        print("labyrinthe généré")
            #connecte = not(self.indices_voisins(caseActu).issubset(cases_non_generees))

    def visibles(self):
        vision = {}
        for case in self.cases:
            vision["droite"] = []
            vision["haut"] = []
            vision["bas"] = []
            vision["gauche"] = []
            position = case.i
            while self.cases[position].voisins[0] == True:
                vision["droite"].append(position)
                position += 1
            position = case.i
            while self.cases[position].voisins[0] == True:
                vision["haut"].append(position)
                position -= self.largeur
            position = case.i
            while self.cases[position].voisins[0] == True:
                vision["gauche"].append(position)
                position -= 1
            position = case.i
            while self.cases[position].voisins[0] == True:
                vision["bas"].append(position)
                position += self.largeur
            case.visibles = vision
    
            





