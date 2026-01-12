#import Laby
from Laby import *
import global_data
import Affichage
from Affichage import Camera
import sys 
import pygame
pygame.init()
import Joueur

def partie(taille_laby=(10,10),mode_de_jeu="solo",
        coul_fond=(255,255,255), coul_bouton_clair=(170,170,170),police_nationale=pygame.font.SysFont('Corbel',35),
        touches = [pygame.K_z, pygame.K_q, pygame.K_s, pygame.K_d],debug=False, ):
    """ boucle principale du jeu. Prend en argument les paramètre graphiques du style"""
    print("lancement d'une partie'")
    # menu principal
    pygame.init() 
    res = (720,720) # taille en pixels de la fenetre
    fenetre = pygame.display.set_mode(res)
    pygame.display.set_caption("Jeu de labyrinthe")
    largeur = taille_laby[1]
    hauteur = taille_laby[0]
    Horloge = pygame.time.Clock()
    fps_max = 60# fps_max

    Labyr = Labyrinthe(largeur,hauteur)
    Labyr.generer_par_Wilson()
    if debug:
        Labyr.afficher_comme_texte()
    Labyr.visibles()

    joueurs = []

    if mode_de_jeu=="solo":
        Labyr.placer_depart(ratio_distance_min=0.7)
        # création du Joueur :
        J1 = Joueur.Joueur(Labyr,Labyr.cases[Labyr.depart],(255,0,0),4,5)
        J1.voir()
        joueurs.append(J1)
    

    if mode_de_jeu=="robot":
        Labyr.placer_deux_joueurs(ratio_eloignement=0.6)
        J1 = Joueur.Joueur(Labyr,Labyr.cases[Labyr.joueur1],(255,0,0),4,5)
        J1.voir()
        joueurs.append(J1)
        BOT = Joueur.Joueur(Labyr,Labyr.cases[Labyr.joueur2],(0,0,255),4,5)
        BOT.voir()
        joueurs.append(BOT)
    

    type_vision = Camera()
    type_vision.centrage=J1
    dimension_min_laby = min(taille_laby[0],taille_laby[1])
    type_vision.hauteur_vision=dimension_min_laby
    type_vision.largeur_vision=dimension_min_laby


    # affichage initial
    #vision_init = Labyr.visibles()
    fenetre.fill((255, 255,255))
    pygame.display.update()



    # boucle principale :
    Sortie = False
    Defaite = False
    duree_totale = 0

    print("lancement de la boucle principale")

    while not Sortie:
        if(pygame.time.get_ticks()>100000):
            Sortie = True
            print("sortie car temps trop long")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Sortie = True
                Defaite = True
            if event.type == pygame.KEYDOWN:
                #on efface la position précédente du joueur et on dessine la nouvelle position
                Affichage.effacer_joueur(fenetre,J1,min(res[0],res[1]),camera=type_vision)
                J1.changement_direction(event.key,touches)
                J1.deplacement()
                J1.voir()

                if(J1.get_case_absolue() == Labyr.sortie):
                    print("Vous avez gagné !")
                    Sortie = True
                
                if len(joueurs)>1:
                    # déplacement du robot
                    Affichage.effacer_joueur(fenetre,BOT,min(res[0],res[1]),camera=type_vision)
                    # stratégie très basique : le robot choisit une direction au hasard parmi celles possibles
                    directions_possibles = []
                    for d in range(4):
                        if BOT._case.voisins[d]:
                            directions_possibles.append(d)
                    if len(directions_possibles)>0:
                        BOT._direction = random.choice(directions_possibles)
                        BOT.deplacement()
                        BOT.voir()
                    
                    if(BOT.get_case_absolue() == Labyr.sortie):
                        print("Le robot a gagné ! Vous avez perdu.")
                        Sortie = True
                        Defaite = True


                    
        # dessin éléments :
        
        Affichage.tout_effacer(fenetre)

        # dessin du labyrinthe total pour débuggage (en BLEU)
        # pour l'instant, l'affichage se fait en position absolue
        #Affichage.affiche_labyrinthe(fenetre,Labyr,min(res[0],res[1]),coul_mur=(0,0,255))

        # dessin des cases déjà vues (en GRIS)
        Affichage.affiche_ensemble_de_cases(fenetre,Labyr,J1.cases_vues,min(res[0],res[1]),coul_mur=(150,150,150),camera=type_vision)

        # dessin des cases vues actuellement (en NOIR)
        Affichage.affiche_ensemble_de_cases(fenetre,Labyr,J1.visu_actuel,min(res[0],res[1]),coul_mur=(0,0,0),camera=type_vision)


        # dessin du joueur en position absolue (en la couleur du joueur)
        for joueur in joueurs:
            Affichage.afficher_joueur(fenetre,joueur,min(res[0],res[1]),camera=type_vision)
        
                    
        #pygame.display.flip()
        pygame.display.update()
        Horloge.tick(fps_max)
        duree_totale += Horloge.get_time()

    if not Defaite:
        affiche_fenetre_fin(duree_totale/1000,victoire=True)
    else:
        affiche_fenetre_fin(duree_totale/1000,victoire=True)
    pygame.display.quit()


def affiche_fenetre_fin(nb_ticks,victoire=True):
    pygame.init() 
    res = (620,220) # taille en pixels de la fenetre
    fenetre = pygame.display.set_mode(res)
    police_nationale = pygame.font.SysFont('Corbel',res[1]//10)
    if victoire:
        texte_fin = police_nationale.render("Vous avez gagné en "+str(nb_ticks)+" secondes !" , True , (0,0,0))
    else:
        texte_fin = police_nationale.render("Vous avez perdu après "+str(nb_ticks)+" secondes !" , True , (0,0,0))
    fenetre.fill((255, 255,255))
    fenetre.blit(texte_fin, (res[0]//10, res[1]//2 - res[1]//10))
    pygame.display.update()
    attente = True
    while attente:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                attente = False
            if event.type == pygame.KEYDOWN:
                attente = False
    pygame.display.quit()

def affiche_fenetre_selection_valeur(texte="Entrez une valeur", valeur_defaut="10"):
    #On ouvre une fenetre qui demande à  l'utilisateur d'entrer la taille du labyrinthe
    fen1 = pygame.display.set_mode((500, 200))
    pygame.display.set_caption(texte)

    # --- Variables ---
    valeur = ""      # Ce que l'utilisateur tape
    active = True        # Tant que la saisie est ouverte
    clock = pygame.time.Clock()

    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                active = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    print("Nombre entré :", valeur)
                    active = False  # fermer la fenêtre ou continuer
                elif event.key == pygame.K_BACKSPACE:
                    valeur = valeur[:-1]
                else:
                    # Ajouter seulement des chiffres
                    if event.unicode.isdigit():
                        valeur += event.unicode

        # --- Affichage ---
        fen1.fill((30, 30, 30))  # gris foncé
        police = pygame.font.SysFont('Corbel',35)
        txt_surface = police.render(texte + (valeur if len(valeur)>0 else ("*"+str(valeur_defaut))), True, (255, 255, 255))
        
        
        fen1.blit(txt_surface, (20, 80))

        pygame.display.update()
        clock.tick(30)

    pygame.display.quit()
    return valeur

if __name__=="__main__":
    test_console = False
    if test_console:
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
    HAUTEUR = 600
    LARGEUR = 750
    res = (LARGEUR,HAUTEUR) 
    fenetre = pygame.display.set_mode(res)
    #largeur = fenetre.get_width()  
    #hauteur = fenetre.get_height() #??
    Horloge = pygame.time.Clock()

    # définition des couleurs et du style :
    coul_fond = (255,255,255) 
    coul_bouton_clair = (200,240,200)

    largeur_rect = LARGEUR//6
    hauteur_rect = HAUTEUR//10
    dist_inter_rect = 10
    
    police_nationale = pygame.font.SysFont('Corbel',res[1]//10) 
    text_click = police_nationale.render("jeu Solo", 1, (0,0,0))
    rect_click = pygame.Rect(LARGEUR//2-largeur_rect//2,HAUTEUR//2-hauteur_rect//2,largeur_rect,hauteur_rect)

    text_VS_robot = police_nationale.render("VS Robot", 1, (100,100,100))
    rect_VS_robot = pygame.Rect(LARGEUR//2-largeur_rect//2,HAUTEUR//2-hauteur_rect//2+dist_inter_rect+hauteur_rect,largeur_rect,hauteur_rect)

    text_quit = police_nationale.render('Quitter' , True , (0,0,0)) 
    rect_quit = pygame.Rect(LARGEUR//2-largeur_rect//2,HAUTEUR//2-hauteur_rect//2+2*dist_inter_rect+2*hauteur_rect,largeur_rect,hauteur_rect)


    
    # affichage des éléments
    image = pygame.image.load("ressources/loading_image.png")
    image = pygame.transform.scale(image, res)

    # boucle principale menu :
    while True:
        for event in pygame.event.get():
            if (event.type == pygame.QUIT or (event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE)
                                        or (event.type==pygame.MOUSEBUTTONUP and rect_quit.collidepoint(pygame.mouse.get_pos()))):
                pygame.quit()
                sys.exit()
            #On detecte si on clique sur la souris, ce qui ferme le menu et lance la partie 
            if ((event.type == pygame.MOUSEBUTTONUP 
                    and (rect_click.collidepoint(pygame.mouse.get_pos())
                         or rect_VS_robot.collidepoint(pygame.mouse.get_pos()))) 
                or (event.type==pygame.KEYDOWN 
                    and (event.key == pygame.K_RETURN or event.key == pygame.K_s
                         or event.key == pygame.K_r))):
                    modeDeJeu = "solo" if ((event.type == pygame.MOUSEBUTTONUP and rect_click.collidepoint(pygame.mouse.get_pos())) 
                       or (event.type==pygame.KEYDOWN 
                    and (event.key == pygame.K_RETURN or event.key == pygame.K_s))) else "robot"
                    pygame.display.quit()
                    hauteur_defaut = 10
                    largeur_defaut = 10
                    hauteur_entree = affiche_fenetre_selection_valeur(texte="hauteur du labyrinthe : ",valeur_defaut=str(hauteur_defaut))
                    largeur_entree = affiche_fenetre_selection_valeur(texte="largeur du labyrinthe : ",valeur_defaut=str(largeur_defaut))
                    
                    if largeur_entree == "":
                        largeur_entree = largeur_defaut
                    if hauteur_entree == "":
                        hauteur_entree = hauteur_defaut
                    
                    partie((int(largeur_entree),int(hauteur_entree)),mode_de_jeu=modeDeJeu)
                    pygame.quit()
                    sys.exit()

        
        #pygame.draw.rect(fenetre, (255, 255,255), rect_click)
        fenetre.blit(image, (0, 0))      
        #affichage du rect (bouton sur lequel est ajouté text) :
        pygame.draw.rect(fenetre, coul_bouton_clair, rect_click)
        fenetre.blit(text_click, (LARGEUR//2-text_click.get_width()//2,HAUTEUR//2-text_click.get_height()//2))
        
        pygame.draw.rect(fenetre, coul_bouton_clair, rect_VS_robot)
        fenetre.blit(text_VS_robot, (LARGEUR//2-text_VS_robot.get_width()//2, rect_VS_robot.y + hauteur_rect//2 - text_VS_robot.get_height()//2))
        
        pygame.draw.rect(fenetre, coul_bouton_clair, rect_quit)
        fenetre.blit(text_quit, (LARGEUR//2-text_quit.get_width()//2, rect_quit.y + hauteur_rect//2 - text_quit.get_height()//2))

        pygame.display.flip()
        Horloge.tick(60)



    pygame.init()
    print("fin du programme")
