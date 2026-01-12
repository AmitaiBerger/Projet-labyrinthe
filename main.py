#import Laby
from Laby import *
import global_data
import Affichage
from Affichage import Camera
import sys 
import pygame
import Joueur
from Network import Network # Import du réseau

pygame.init()

def partie(taille_laby=(10,10), mode_de_jeu="solo", ip_serveur="localhost",
        coul_fond=(255,255,255), coul_bouton_clair=(170,170,170),police_nationale=pygame.font.SysFont('Corbel',35),
        touches = [pygame.K_z, pygame.K_q, pygame.K_s, pygame.K_d], debug=False):
    
    print(f"lancement d'une partie en mode {mode_de_jeu}")
    pygame.init() 
    res = (720,720)
    fenetre = pygame.display.set_mode(res)
    pygame.display.set_caption("Jeu de labyrinthe")
    Horloge = pygame.time.Clock()
    fps_max = 60

    joueurs = []
    mon_id = 0
    reseau = None
    
    # --- CONFIGURATION INITIALE ---
    if mode_de_jeu == "reseau":
        # Ecran de chargement
        fenetre.fill((255,255,255))
        txt = police_nationale.render("Connexion au serveur...", True, (0,0,0))
        fenetre.blit(txt, (res[0]//2 - txt.get_width()//2, res[1]//2))
        pygame.display.update()

        reseau = Network(ip_serveur)
        if reseau.p is None:
            return # Echec connexion

        Labyr, mon_id = reseau.p
        Labyr.visibles()
        
        # Création des joueurs
        J1_obj = Joueur.Joueur(Labyr, Labyr.cases[Labyr.joueur1], (255,0,0), 4, 5)
        J2_obj = Joueur.Joueur(Labyr, Labyr.cases[Labyr.joueur2], (0,0,255), 4, 5)
        
        if mon_id == 0:
            J_Moi = J1_obj
            J_Autre = J2_obj
            coul_moi = (255, 0, 0)
        else:
            J_Moi = J2_obj
            J_Autre = J1_obj
            coul_moi = (0, 0, 255)

        joueurs.append(J_Moi)
        joueurs.append(J_Autre)
        J_Moi.voir()
        
        largeur = Labyr.largeur
        hauteur = Labyr.hauteur

    else:
        # Code existant pour SOLO / ROBOT
        largeur = taille_laby[1]
        hauteur = taille_laby[0]
        Labyr = Labyrinthe(largeur,hauteur)
        Labyr.generer_par_Wilson()
        Labyr.visibles()
        if mode_de_jeu=="solo":
            Labyr.placer_depart(ratio_distance_min=0.7)
            J1 = Joueur.Joueur(Labyr,Labyr.cases[Labyr.depart],(255,0,0),4,5)
            J1.voir()
            joueurs.append(J1)
            J_Moi = J1
        if mode_de_jeu=="robot":
            Labyr.placer_deux_joueurs(ratio_eloignement=0.6)
            J1 = Joueur.Joueur(Labyr,Labyr.cases[Labyr.joueur1],(255,0,0),4,5)
            J1.voir()
            joueurs.append(J1)
            BOT = Joueur.Joueur(Labyr,Labyr.cases[Labyr.joueur2],(0,0,255),4,5)
            joueurs.append(BOT)
            J_Moi = J1

    # --- CAMÉRA ---
    type_vision = Camera()
    type_vision.centrage = J_Moi
    
    if mode_de_jeu == "reseau":
        type_vision.hauteur_vision = 12
        type_vision.largeur_vision = 12
    else:
        type_vision.hauteur_vision = min(hauteur, largeur)
        type_vision.largeur_vision = min(hauteur, largeur)

    # BOUCLE PRINCIPALE
    Sortie = False
    Defaite = False
    GameStatus = "PLAY" # Par défaut PLAY pour le solo
    duree_totale = 0
    message_attente = "En attente du joueur 2..."

    while not Sortie:
        # 1. GESTION RÉSEAU
        can_move = True
        
        if mode_de_jeu == "reseau":
            try:
                # Envoi position -> Réception (Pos_Autre, Status)
                reponse = reseau.send(J_Moi.get_case_absolue())
                
                if reponse:
                    pos_autre, GameStatus = reponse
                    J_Autre.set_case_absolue(pos_autre)
                    
                    if GameStatus == "WAIT":
                        can_move = False
                    elif GameStatus == "WIN":
                        # J'ai gagné (le serveur confirme)
                        Sortie = True
                        Defaite = False
                    elif GameStatus == "LOSE":
                        # L'autre a gagné
                        Sortie = True
                        Defaite = True
                        
            except Exception as e:
                print("Erreur réseau:", e)
                Sortie = True

        # 2. EVENTS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Sortie = True
                Defaite = True # Quitter = perdre/abandonner
            
            if event.type == pygame.KEYDOWN and can_move:
                Affichage.effacer_joueur(fenetre, J_Moi, min(res[0],res[1]), camera=type_vision)
                J_Moi.changement_direction(event.key, touches)
                J_Moi.deplacement()
                J_Moi.voir()

                # Victoire Solo / Robot (Gestion locale)
                if mode_de_jeu != "reseau" and J_Moi.get_case_absolue() == Labyr.sortie:
                    Sortie = True
                    Defaite = False

        # 3. AFFICHAGE
        Affichage.tout_effacer(fenetre)

        if mode_de_jeu == "reseau" and not can_move:
            # Écran d'attente
            police_attente = pygame.font.SysFont('Corbel', 50)
            txt = police_attente.render(message_attente, True, (0,0,0))
            fenetre.blit(txt, (res[0]//2 - txt.get_width()//2, res[1]//2))
        else:
            # Jeu normal
            Affichage.affiche_ensemble_de_cases(fenetre,Labyr,J_Moi.cases_vues,min(res[0],res[1]),coul_mur=(150,150,150),camera=type_vision)
            Affichage.affiche_ensemble_de_cases(fenetre,Labyr,J_Moi.visu_actuel,min(res[0],res[1]),coul_mur=(0,0,0),camera=type_vision)
            
            for joueur in joueurs:
                Affichage.afficher_joueur(fenetre,joueur,min(res[0],res[1]),camera=type_vision)

        pygame.display.update()
        Horloge.tick(fps_max)
        if can_move:
            duree_totale += Horloge.get_time()

    # FIN DE PARTIE
    if mode_de_jeu == "reseau":
        reseau.close() # Important : on coupe la connexion pour que le serveur reset
    
    if not Defaite:
        affiche_fenetre_victoire(duree_totale/1000)
    elif mode_de_jeu == "reseau":
        # Petit écran de défaite rapide
        affiche_fenetre_defaite()
        
    # Retour au menu (pygame.display.quit n'est pas appelé ici pour garder le menu actif)

def affiche_fenetre_defaite():
    res = (620,220) 
    fenetre = pygame.display.set_mode(res)
    police = pygame.font.SysFont('Corbel',res[1]//10) 
    texte = police.render("Perdu ! L'adversaire a gagné.", True , (200,0,0))
    fenetre.fill((255, 255,255))
    fenetre.blit(texte, (res[0]//10, res[1]//2 - res[1]//10))
    pygame.display.update()
    pygame.time.delay(3000) # Attendre 3 secondes puis quitter

def affiche_fenetre_victoire(nb_ticks):
    # pygame.init() # Déjà init
    res = (620,220) 
    fenetre = pygame.display.set_mode(res)
    police_nationale = pygame.font.SysFont('Corbel',res[1]//10) 
    texte_victoire = police_nationale.render("Victoire en "+str(round(nb_ticks, 2))+" s !" , True , (0,0,0))
    fenetre.fill((255, 255,255))
    fenetre.blit(texte_victoire, (res[0]//10, res[1]//2 - res[1]//10))
    pygame.display.update()
    attente = True
    while attente:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                attente = False
            if event.type == pygame.KEYDOWN:
                attente = False

def affiche_fenetre_selection_valeur(texte="Entrez une valeur", valeur_defaut="10"):
    fen1 = pygame.display.set_mode((500, 200))
    pygame.display.set_caption(texte)
    valeur = ""
    active = True
    clock = pygame.time.Clock()

    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                active = False
                return valeur_defaut # Sécurité
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    active = False
                elif event.key == pygame.K_BACKSPACE:
                    valeur = valeur[:-1]
                else:
                    valeur += event.unicode # Accepte tout texte (IP)

        fen1.fill((30, 30, 30))
        police = pygame.font.SysFont('Corbel',35)
        txt_surface = police.render(texte + (valeur if len(valeur)>0 else ("*"+str(valeur_defaut))), True, (255, 255, 255))
        fen1.blit(txt_surface, (20, 80))
        pygame.display.update()
        clock.tick(30)
    return valeur if valeur != "" else valeur_defaut

if __name__=="__main__":
    # menu principal
    pygame.init() 
    HAUTEUR = 600
    LARGEUR = 750
    res = (LARGEUR,HAUTEUR) 
    fenetre = pygame.display.set_mode(res)
    Horloge = pygame.time.Clock()

    coul_fond = (255,255,255) 
    coul_bouton_clair = (200,240,200)
    coul_bouton_reseau = (200,200,240)

    largeur_rect = LARGEUR//6
    hauteur_rect = HAUTEUR//10
    dist_inter_rect = 10
    
    police_nationale = pygame.font.SysFont('Corbel',res[1]//10) 
    
    # Boutons
    text_click = police_nationale.render("Jeu Solo", 1, (0,0,0))
    rect_click = pygame.Rect(LARGEUR//2-largeur_rect//2,HAUTEUR//2-hauteur_rect//2 - hauteur_rect, largeur_rect,hauteur_rect)

    text_VS_robot = police_nationale.render("VS Robot", 1, (100,100,100))
    rect_VS_robot = pygame.Rect(LARGEUR//2-largeur_rect//2,HAUTEUR//2-hauteur_rect//2+dist_inter_rect,largeur_rect,hauteur_rect)

    text_Reseau = police_nationale.render("Reseau", 1, (0,0,0))
    rect_Reseau = pygame.Rect(LARGEUR//2-largeur_rect//2,HAUTEUR//2-hauteur_rect//2+2*dist_inter_rect+hauteur_rect,largeur_rect,hauteur_rect)

    text_quit = police_nationale.render('Quitter' , True , (0,0,0)) 
    rect_quit = pygame.Rect(LARGEUR//2-largeur_rect//2,HAUTEUR//2-hauteur_rect//2+3*dist_inter_rect+2*hauteur_rect,largeur_rect,hauteur_rect)
    
    image = pygame.image.load("ressources/loading_image.png")
    image = pygame.transform.scale(image, res)

    while True:
        # Réinitialisation de l'affichage du menu
        #fenetre = pygame.display.set_mode(res)
        
        for event in pygame.event.get():
            if (event.type == pygame.QUIT or (event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE)):
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                
                # --- SOLO ---
                if rect_click.collidepoint(pos):
                    hauteur_entree = affiche_fenetre_selection_valeur("hauteur : ", "10")
                    largeur_entree = affiche_fenetre_selection_valeur("largeur : ", "10")
                    partie((int(largeur_entree),int(hauteur_entree)), mode_de_jeu="solo")
                    # Retour au menu après la partie
                    fenetre = pygame.display.set_mode(res) 

                # --- ROBOT ---
                elif rect_VS_robot.collidepoint(pos):
                    hauteur_entree = affiche_fenetre_selection_valeur("hauteur : ", "10")
                    largeur_entree = affiche_fenetre_selection_valeur("largeur : ", "10")
                    partie((int(largeur_entree),int(hauteur_entree)), mode_de_jeu="robot")
                    fenetre = pygame.display.set_mode(res)

                # --- RÉSEAU ---
                elif rect_Reseau.collidepoint(pos):
                    ip = affiche_fenetre_selection_valeur("IP Serveur : ", "localhost")
                    partie((10,10), mode_de_jeu="reseau", ip_serveur=ip)
                    fenetre = pygame.display.set_mode(res)

                # --- QUITTER ---
                elif rect_quit.collidepoint(pos):
                    pygame.quit()
                    sys.exit()

        fenetre.blit(image, (0, 0))      
        
        pygame.draw.rect(fenetre, coul_bouton_clair, rect_click)
        fenetre.blit(text_click, (LARGEUR//2-text_click.get_width()//2, rect_click.y + hauteur_rect//2 - text_click.get_height()//2))
        
        pygame.draw.rect(fenetre, coul_bouton_clair, rect_VS_robot)
        fenetre.blit(text_VS_robot, (LARGEUR//2-text_VS_robot.get_width()//2, rect_VS_robot.y + hauteur_rect//2 - text_VS_robot.get_height()//2))
        
        pygame.draw.rect(fenetre, coul_bouton_reseau, rect_Reseau)
        fenetre.blit(text_Reseau, (LARGEUR//2-text_Reseau.get_width()//2, rect_Reseau.y + hauteur_rect//2 - text_Reseau.get_height()//2))
        
        pygame.draw.rect(fenetre, coul_bouton_clair, rect_quit)
        fenetre.blit(text_quit, (LARGEUR//2-text_quit.get_width()//2, rect_quit.y + hauteur_rect//2 - text_quit.get_height()//2))

        pygame.display.flip()
        Horloge.tick(60)