import random


class Case():

    def __init__(self):
        self.voisins = [None,None,None,None]# booléen pour si la case est connectée aux voisins
        self.contenu = None
    


class Laby():

    def __init__(self,hauteur,largeur):
        self.cases = []
        self.largeur=largeur
        self.hauteur=hauteur
    
    def indices_voisins(self,indice_centre:int):
        vois = []
        if not (indice_centre%self.largeur==0):# (à gauche)
            vois.append(indice_centre-1)
        if not (indice_centre%self.largeur==self.largeur-1):
            vois.append(indice_centre+1)
        if not (indice_centre/self.largeur==0): # en haut
            vois.append(indice_centre+self.largeur)
        if not (indice_centre/self.largeur==self.hauteur-1):# on n'est pas en bas
            vois.append(indice_centre-self.largeur)
    
    def generer_par_Wilson(self):
        cases_non_generees = [i for i in range(self.largeur*self.hauteur)]
        while(len(self.cases)<self.hauteur*self.largeur):
            caseActu = random.choice(cases_non_generees)
            connecte = (self.indices_voisins(caseActu).is)




