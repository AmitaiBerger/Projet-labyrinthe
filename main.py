#import Laby
from Laby import *

if __name__=="__main__":
    Labyr = Labyrinthe(10,10)
    Labyr.generer_par_Wilson()
    print("coordonnées 5,5 :", Labyr.cases[5*Labyr.largeur+5].voisins)
    Labyr.afficher_comme_texte()
    Labyr.visibles()
    print("vision  depuis la case 5,5 :", Labyr.cases[5*Labyr.largeur+5].visibles)

    print("fin du programme")
