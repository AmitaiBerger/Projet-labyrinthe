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
            


            if(set(self.indices_voisins(caseActu)).issubset(set(cases_non_generees))):
                # si aucun des voisins n'est déjà dans le labyrinthe
                connecte = False
                cheminActu = [caseActu]
                while not connecte:# on fait une marche aléatoire vers le Laby déjà généré
                    prochain = random.choice(self.indices_voisins(cheminActu[len(cheminActu)-1]))
                    if(prochain in cheminActu):# si on fait une boucle, on supprime la boucle
                        for i in range(cheminActu.index(prochain)+1,len(cheminActu)-1):
                            cheminActu.pop()
                    elif(prochain in self.cases):# si on rejoint le labyrinthe
                        casesCheminActu=[]
                        for j in range(len(cheminActu)):
                            casesCheminActu.append(Case(cheminActu[j]))
                            cases_non_generees.remove(cheminActu[j])
                        casesCheminActu[0].voisins.append(cheminActu[1])
                        for i in range(1,len(cheminActu)-1):
                            cheminActu[i].voisins.append(cheminActu[i+1])
                            cheminActu[i].voisins.append(cheminActu[i-1])
                        cheminActu[len(cheminActu)-1].voisins.append(cheminActu[i-2])
                        self.cases = self.cases+cheminActu
                        connecte=True
                    else:
                        cheminActu.append(prochain)
            else:# alors un voisin de caseActu est deja dans le labyrinthe
                CaseActu = Case(caseActu) # un crée un objet Case à la place de l'indice
                self.cases.append(CaseActu)
                for j in self.indices_voisins(caseActu):# on lui ajoute ses voisins
                    if len(CaseActu.voisins)==0:
                        for Casee in self.cases:
                            if len(CaseActu.voisins)==0:
                                if j==Casee.j:
                                    CaseActu.voisins.append(Casee)

            
                
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
    
            





