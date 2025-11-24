#import Laby
from Laby import *
import global_data
import Affichage
import sys 
import pygame

def partie():
    print("lancement d'une partie'")


if __name__=="__main__":
    Labyr = Labyrinthe(10,10)
    Labyr.generer_par_Wilson()
    print("coordonnées 5,5 :", Labyr.cases[5*Labyr.largeur+5].voisins)
    Labyr.afficher_comme_texte()
    Labyr.visibles()
    print("vision  depuis la case 5,5 :", Labyr.cases[5*Labyr.largeur+5].visibles)
    print("vision  depuis la case 4,4 :", Labyr.cases[4*Labyr.largeur+4].visibles)

    # menu principal
    pygame.init() 
    res = (720,720) 
    fenetre = pygame.display.set_mode(res)
    largeur = fenetre.get_width()  
    hauteur = fenetre.get_height() 
    Horloge = pygame.time.Clock()

    # définition des couleurs et du style :
    coul_fond = (255,255,255) 
    coul_bouton_clair = (170,170,170)
    rect = pygame.Rect(100,100,100,50)
    police_nationale = pygame.font.SysFont('Corbel',35) 
    click = police_nationale.render("Click me", 1, (0,0,0))

    # affichage des éléments
    text = police_nationale.render('quit' , True , coul_fond) 

    # boulce principale menu :
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                if rect.collidepoint(pygame.mouse.get_pos()):
                    Fenetre()
        pygame.draw.rect(fenetre, (255, 255,255), rect)
        fenetre.blit(click, rect)
        pygame.display.flip()
        Horloge.tick(60)



    pygame.init()
    print("fin du programme")
