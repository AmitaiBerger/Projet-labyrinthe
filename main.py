#import Laby
from Laby import *
import global_data
import Affichage
import sys 
import pygame
pygame.init()
import Joueur

def partie(taille_laby=(10,10),
        coul_fond=(255,255,255), coul_bouton_clair=(170,170,170),police_nationale=pygame.font.SysFont('Corbel',35),
        touches = [pygame.K_z, pygame.K_q, pygame.K_s, pygame.K_d]):
    """ boucle principale du jeu. Prend en argument les paramètre graphiques du style"""
    print("lancement d'une partie'")
    # menu principal
    pygame.init() 
    res = (720,720) 
    fenetre = pygame.display.set_mode(res)
    largeur = fenetre.get_width()  
    hauteur = fenetre.get_height() 
    fenetre.fill((255, 255, 255))
    Horloge = pygame.time.Clock()

    Labyr = Labyrinthe(10,10)
    Labyr.generer_par_Wilson()

    # création du Joueur :
    J1 = Joueur.Joueur(Labyr,Labyr.cases[0],(255,0,0),4,5)

    # affichage initial
    #vision_init = Labyr.visibles()


    # boucle principale :
    Sortie = False

    while not Sortie:
        if(pygame.time.get_ticks()>10000):
            Sortie = True
            print("sortie car temps trop long")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # FERME LA FENTRE ET REOUVRE LE MENU
                pygame.quit()
                sys.exit()
            #if event.type == pygame.MOUSEBUTTONUP:
                #if rect.collidepoint(pygame.mouse.get_pos()):

            if event.type == pygame.KEYDOWN:
                if event.key in touches:
                    J1.tourner_suivant_key_ou_deplacer(event.key)
                    J1.visu_actuel = Labyr.visibles(J1.labyrinthe,J1._case.i)
                    J1.cases_vues = J1.cases_vues.union(J1.visu_actuel)

                    
        # dessin éléments :
        
        # dessin du labyrinthe total pour débuggage (en BLEU)
        # pour l'instant, l'affichage se fait en position absolue
        Affichage.affiche_labyrinthe(fenetre,Labyr,min(largeur,hauteur),coul_mur=(0,0,255))

        # dessin des cases déjà vues (en GRIS)
        Affichage.affiche_ensemble_de_cases(fenetre,Labyr,J1.cases_vues,min(largeur,hauteur),coul_mur=(150,150,150))

        # dessin des cases vues actuellement (en NOIR)
        Affichage.affiche_ensemble_de_cases(fenetre,Labyr,J1.visu_actuel,min(largeur,hauteur),coul_mur=(0,0,0))


        # dessin du joueur en position absolue (en la couleur du joueur)
        Affichage.affiche_joueur(fenetre,J1,min(largeur,hauteur))
                    
        pygame.display.flip()
        Horloge.tick(60)



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

    # boucle principale menu :
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            #On detecte si on clique sur la souris, ce qui ferme le menu et lance la partie 
            if event.type == pygame.MOUSEBUTTONUP:
                if rect.collidepoint(pygame.mouse.get_pos()):
                    #pygame.quit()
                    # Demande à  l'utilisateur d'entrer la taille du labyrinthe
                    print("Choisissez une longueur de labyrinthe")
                    longueur=""
                    running = True
                    while running:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                running = False

                            if event.type == pygame.KEYDOWN:

                                # L'utilisateur tape un chiffre (0-9)
                                if event.unicode.isdigit():
                                    longueur += event.unicode

                                # Effacer un chiffre (BACKSPACE)
                                if event.key == pygame.K_BACKSPACE:
                                    longueur = longueur[:-1]

                                # Valider avec ENTER
                                if event.key == pygame.K_RETURN:
                                    if longueur != "":
                                        valeur = int(longueur)  # conversion
                                
                    print("Choisissez une largeur de labyrinthe")

                    largeur=""
                    running2 = True
                    while running2:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                running2 = False

                            if event.type == pygame.KEYDOWN:

                                # L'utilisateur tape un chiffre (0-9)
                                if event.unicode.isdigit():
                                    largeur += event.unicode

                                # Effacer un chiffre (BACKSPACE)
                                if event.key == pygame.K_BACKSPACE:
                                    largeur = largeur[:-1]

                                # Valider avec ENTER
                                if event.key == pygame.K_RETURN:
                                    if largeur != "":
                                        valeur = int(largeur)  # conversion
                                    running2=False

                    
                    if largeur!="" and longueur!="":
                        partie((largeur,longueur))
                    else:
                        partie()

                    
        pygame.draw.rect(fenetre, (255, 255,255), rect)
        fenetre.blit(click, rect)
        pygame.display.flip()
        Horloge.tick(60)



    pygame.init()
    print("fin du programme")
