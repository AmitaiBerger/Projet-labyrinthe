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
    pygame.display.set_caption("Jeu de labyrinthe")
    largeur = taille_laby[1]
    longueur = taille_laby[0]
    Horloge = pygame.time.Clock()

    Labyr = Labyrinthe(largeur,longueur)
    Labyr.generer_par_Wilson()
    Labyr.afficher_comme_texte()
    Labyr.visibles()

    # création du Joueur :
    J1 = Joueur.Joueur(Labyr,Labyr.cases[0],(255,0,0),4,5)

    # affichage initial
    #vision_init = Labyr.visibles()
    fenetre.fill((255, 255,255))
    pygame.display.update()


    # boucle principale :
    Sortie = False

    print("lancement de la boucle principale")

    while not Sortie:
        if(pygame.time.get_ticks()>100000):
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
        Affichage.affiche_labyrinthe(fenetre,Labyr,min(res[0],res[1]),coul_mur=(0,0,255))

        # dessin des cases déjà vues (en GRIS)
        Affichage.affiche_ensemble_de_cases(fenetre,Labyr,J1.cases_vues,min(res[0],res[1]),coul_mur=(150,150,150))

        # dessin des cases vues actuellement (en NOIR)
        Affichage.affiche_ensemble_de_cases(fenetre,Labyr,J1.visu_actuel,min(res[0],res[1]),coul_mur=(0,0,0))


        # dessin du joueur en position absolue (en la couleur du joueur)
        Affichage.affiche_joueur(fenetre,J1,min(res[0],res[1]))
                    
        #pygame.display.flip()
        pygame.display.update()
        Horloge.tick(60)



if __name__=="__main__":
    Labyr = Labyrinthe(10,10)
    Labyr.generer_par_Wilson()
    #Labyr.creuser_trous()
    Labyr.creuser_trous_intelligents(longueur_max_probabilite=5)
    #Labyr.placer_depart(ratio_distance_min=0.7)
    Labyr.placer_deux_joueurs(ratio_eloignement=0.6)
    #Labyr.creuser_trous_organiques(seuil_min=6, longueur_ref=20)
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
                    pygame.display.quit()
                    
                    #On ouvre une fenetre qui demande à  l'utilisateur d'entrer la taille du labyrinthe
                    fen1 = pygame.display.set_mode((500, 200))
                    pygame.display.set_caption("Choisissez une longueur de labyrinthe")

                    # --- Variables ---
                    longueur = ""      # Ce que l'utilisateur tape
                    active = True        # Tant que la saisie est ouverte
                    clock = pygame.time.Clock()

                    while active:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                active = False

                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_RETURN:
                                    print("Nombre entré :", longueur)
                                    active = False  # fermer la fenêtre ou continuer
                                elif event.key == pygame.K_BACKSPACE:
                                    longueur = longueur[:-1]
                                else:
                                    # Ajouter seulement des chiffres
                                    if event.unicode.isdigit():
                                        longueur += event.unicode

                        # --- Affichage ---
                        fen1.fill((30, 30, 30))  # gris foncé

                        txt_surface = police_nationale.render("Choisissez une longueur : " + longueur, True, (255, 255, 255))
                        fen1.blit(txt_surface, (20, 80))

                        pygame.display.update()
                        clock.tick(30)

                    pygame.display.quit()
                    fen2 = pygame.display.set_mode((500, 200))   
                    pygame.display.set_caption("Choisissez une largeur de labyrinthe")
                    # --- Variables ---
                    largeur = ""      # Ce que l'utilisateur tape
                    active = True        # Tant que la saisie est ouverte
                    clock = pygame.time.Clock()

                    while active:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                active = False

                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_RETURN:
                                    print("Nombre entré :", largeur)
                                    active = False  # fermer la fenêtre ou continuer
                                elif event.key == pygame.K_BACKSPACE:
                                    largeur = largeur[:-1]
                                else:
                                    # Ajouter seulement des chiffres
                                    if event.unicode.isdigit():
                                        largeur += event.unicode

                        # --- Affichage ---
                        fen2.fill((30, 30, 30))  # gris foncé

                        txt_surface = police_nationale.render("Choisissez une largeur: " + largeur, True, (255, 255, 255))
                        fen2.blit(txt_surface, (20, 80))

                        pygame.display.update()
                        clock.tick(30)


                    pygame.display.quit()
                    if largeur!="" and longueur!="":
                        largeur=int(largeur)
                        longueur=int(longueur)
                        partie((largeur,longueur))
                    else:
                        partie()

                    
        pygame.draw.rect(fenetre, (255, 255,255), rect)
        fenetre.blit(click, rect)
        pygame.display.flip()
        Horloge.tick(60)



    pygame.init()
    print("fin du programme")
