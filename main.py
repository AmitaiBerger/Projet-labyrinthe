#import Laby
from Laby import *
import config_globale
import Affichage
from Affichage import Camera
import sys 
import pygame
pygame.init()
import Joueur
from dataclasses import dataclass
from enum import Enum
from typing import Union

import pygame
import sys
import threading
import socket
import time
from config import *
from Reseau import Reseau
import serveur as serveur_module


class Type_Joueur(Enum):
    HUMAIN = 1
    ROBOT_ALEATOIRE = 2
    ROBOT_EXPLORATEUR =3


@dataclass
class Parametres:
    joueurs:list[Union[Type_Joueur,tuple[Type_Joueur, float]]]#=[Type_Joueur.HUMAIN]
    touches:list[type(pygame.K_z)]# = [pygame.K_RIGHT,pygame.K_UP,pygame.K_LEFT,pygame.K_DOWN]

    #param graphiques
    coul_fond:tuple[int,int,int]=(255,255,255)
    coul_bouton_clair:tuple[int,int,int]=(170,170,170)
    police_nationale:type(pygame.font.SysFont)=pygame.font.SysFont('Corbel',35)
    debug:bool=False

def obtenir_ip_locale():
    """Récupère l'adresse IP locale de la machine"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 1))
        ip = s.getsockname()[0]
    except:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def afficher_fenetre_ip():
    """Fenêtre pour saisir l'adresse IP du serv"""
    pygame.init()
    fenetre = pygame.display.set_mode((500, 200))
    pygame.display.set_caption("Connexion au serveur")
    
    ip_saisie = "localhost"
    saisie_active = True
    police = pygame.font.SysFont('Corbel', 30)
    clock = pygame.time.Clock()
    
    while saisie_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                saisie_active = False
                return None
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    saisie_active = False
                elif event.key == pygame.K_BACKSPACE:
                    ip_saisie = ip_saisie[:-1]
                elif event.key == pygame.K_ESCAPE:
                    return None
                else:
                    ip_saisie += event.unicode
        
        fenetre.fill((30, 30, 30))
        texte = police.render(f"IP du serveur: {ip_saisie}", True, (255, 255, 255))
        instruction = police.render("Appuyez sur ENTRÉE pour valider", True, (200, 200, 200))
        
        fenetre.blit(texte, (20, 80))
        fenetre.blit(instruction, (20, 120))
        pygame.display.update()
        clock.tick(30)
    
    pygame.display.quit()
    return ip_saisie

def afficher_fenetre_nb_joueurs():
    """Fenêtre pour choisir le nombre de joueurs"""
    pygame.init()
    fenetre = pygame.display.set_mode((500, 200))
    pygame.display.set_caption("Nombre de joueurs")
    
    nb_saisi = "2"
    saisie_active = True
    police = pygame.font.SysFont('Corbel', 30)
    clock = pygame.time.Clock()
    
    while saisie_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                saisie_active = False
                return None
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if nb_saisi.isdigit() and 2 <= int(nb_saisi) <= 9:
                        saisie_active = False
                elif event.key == pygame.K_BACKSPACE:
                    nb_saisi = nb_saisi[:-1]
                elif event.key == pygame.K_ESCAPE:
                    return None
                elif event.unicode.isdigit():
                    nb_saisi += event.unicode
        
        fenetre.fill((30, 30, 30))
        texte = police.render(f"Nombre de joueurs (2-9): {nb_saisi}", True, (255, 255, 255))
        instruction = police.render("Appuyez sur ENTRÉE pour valider", True, (200, 200, 200))
        
        fenetre.blit(texte, (20, 80))
        fenetre.blit(instruction, (20, 120))
        pygame.display.update()
        clock.tick(30)
    
    pygame.display.quit()
    return int(nb_saisi) if nb_saisi.isdigit() else 2

def heberger():
    """Lance un serveur local et s'y connecte'"""
    nb_joueurs = afficher_fenetre_nb_joueurs()
    if nb_joueurs is None:
        return
    
    # Lance le serveur dans un thread séparé
    serveur_thread = threading.Thread(target=serveur_module.lancer_serveur, args=(nb_joueurs,))
    serveur_thread.daemon = True
    serveur_thread.start()
    
    # Attend un peu que le serveur démarre
    time.sleep(0.5)
    
    # Se connecte au serveur local
    ip_locale = obtenir_ip_locale()
    reseau = Reseau("localhost", 5555)
    
    if reseau.data_initiale is None:
        print("Erreur: Impossible de se connecter au serveur local")
        return
    
    # Lance la partie en réseau
    partie_reseau(reseau)

def se_connecter():
    """à un serveur existant"""
    ip = afficher_fenetre_ip()
    if ip is None:
        return
    
    reseau = Reseau(ip, 5555)
    
    if reseau.data_initiale is None:
        print(f"Erreur: Impossible de se connecter à {ip}")
        return
    
    # Lance la partie en réseau
    partie_reseau(reseau)

def partie_reseau(reseau):
    """Boucle principale pour le mode multijoueur en réseau"""
    print("Lancement d'une partie multijoueur en réseau")
    
    # Récupère les données initiales du serveur
    labyrinthe, mon_id, nb_joueurs_total = reseau.data_initiale
    
    # Initialisation Pygame
    pygame.init()
    res = (720, 720)
    fenetre = pygame.display.set_mode(res)
    pygame.display.set_caption("Jeu de labyrinthe - Multijoueur")
    Horloge = pygame.time.Clock()
    fps_max = 60
    
    # Crée les objets joueurs
    joueurs = []
    couleurs = [(255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 255, 0), 
                (255, 0, 255), (0, 255, 255), (255, 128, 0), (128, 0, 255), (128, 128, 128)]
    
    for i in range(nb_joueurs_total):
        case_depart = labyrinthe.joueurs_indices_depart[i] if i < len(labyrinthe.joueurs_indices_depart) else 0
        couleur = couleurs[i % len(couleurs)]
        joueur = Joueur.Joueur(labyrinthe, labyrinthe.cases[case_depart], couleur, 4, 5)
        joueur.voir()
        joueurs.append(joueur)
    
    joueur_local = joueurs[mon_id]
    
    # Configuration de la caméra
    camera = Camera()
    camera.centrage = joueur_local
    dimension_min_laby = min(labyrinthe.hauteur, labyrinthe.largeur)
    camera.hauteur_vision = dimension_min_laby
    camera.largeur_vision = dimension_min_laby
    
    # Variables du jeu
    Sortie = False
    statut_jeu = "WAIT"  # WAIT, PLAY, WIN, LOSE
    evenements_traites = set()
    
    print("Attente des autres joueurs...")
    
    # Boucle principale
    while not Sortie:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Sortie = True
            if event.type == pygame.KEYDOWN and statut_jeu == "PLAY":
                # Gestion des déplacements
                ancienne_case = joueur_local.get_case_absolue()
                Affichage.effacer_joueur(fenetre, joueur_local, min(res[0], res[1]), camera=camera)
                joueur_local.changement_direction(event.key, [pygame.K_RIGHT, pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN])
                joueur_local.deplacement()
                joueur_local.voir()
                
                # Envoi du mouvement au serveur
                nouvelle_case = joueur_local.get_case_absolue()
                if nouvelle_case != ancienne_case:
                    # Vérifie si un item a été pris
                    item_pris = None
                    if nouvelle_case in labyrinthe.items:
                        item_pris = nouvelle_case
                    
                    reseau.send(("MOVE", nouvelle_case, item_pris))
        
        # Réception des données du serveur
        try:
            reponse = reseau.send(joueur_local.get_case_absolue())
            if reponse:
                positions, statut, nb_connectes, evenements = reponse
                statut_jeu = statut
                
                # Met à jour les positions de tous les joueurs
                for i, pos in enumerate(positions):
                    if i < len(joueurs):
                        joueurs[i].case = labyrinthe.cases[pos]
                        joueurs[i].case_absolue = pos
                
                # Traite les événements
                for evt in evenements:
                    signature = str(evt)
                    if signature not in evenements_traites:
                        evenements_traites.add(signature)
                        if evt[0] == "ITEM_GONE":
                            idx_item = evt[1]
                            if idx_item in labyrinthe.items:
                                del labyrinthe.items[idx_item]
                        elif evt[0] == "WALL_BROKEN":
                            idx, direction = evt[1], evt[2]
                            labyrinthe.cases[idx].voisins[direction] = True
                            # Ouvre le mur opposé
                            if direction == 0: idx_oppose = idx + 1
                            elif direction == 1: idx_oppose = idx - labyrinthe.largeur
                            elif direction == 2: idx_oppose = idx - 1
                            elif direction == 3: idx_oppose = idx + labyrinthe.largeur
                            
                            if 0 <= idx_oppose < len(labyrinthe.cases):
                                labyrinthe.cases[idx_oppose].voisins[(direction + 2) % 4] = True
            else:
                print("Connexion perdue")
                Sortie = True
        except Exception as e:
            print(f"Erreur réseau: {e}")
            Sortie = True
        
        # Mise à jour de la vision
        joueur_local.visu_actuel = set([joueur_local.get_case_absolue()])
        labyrinthe.calculer_visibilite()
        case_actuelle = labyrinthe.cases[joueur_local.get_case_absolue()]
        for direction in case_actuelle.visibles:
            joueur_local.visu_actuel.update(case_actuelle.visibles[direction])
        joueur_local.cases_vues.update(joueur_local.visu_actuel)
        
        # Affichage
        Affichage.tout_effacer(fenetre)
        
        # Cases déjà vues (gris)
        Affichage.affiche_ensemble_de_cases(fenetre, labyrinthe, joueur_local.cases_vues,
                                            min(res[0], res[1]), coul_mur=(150, 150, 150), camera=camera)
        
        # Cases vues actuellement (noir)
        Affichage.affiche_ensemble_de_cases(fenetre, labyrinthe, joueur_local.visu_actuel,
                                            min(res[0], res[1]), coul_mur=(0, 0, 0), camera=camera)
        
        # Affichage des joueurs
        for joueur in joueurs:
            Affichage.afficher_joueur(fenetre, joueur, min(res[0], res[1]), camera=camera)
        
        # Affichage du statut
        police = pygame.font.SysFont('Corbel', 24)
        if statut_jeu == "WAIT":
            texte = police.render(f"En attente des joueurs... ({nb_connectes}/{nb_joueurs_total})", True, (0, 0, 0))
            fenetre.blit(texte, (10, 10))
        elif statut_jeu == "PLAY":
            texte = police.render("Partie en cours", True, (0, 0, 0))
            fenetre.blit(texte, (10, 10))
        elif statut_jeu == "WIN":
            texte = police.render("VICTOIRE !", True, (0, 255, 0))
            fenetre.blit(texte, (res[0] // 2 - 50, 10))
        elif statut_jeu == "LOSE":
            texte = police.render("Défaite...", True, (255, 0, 0))
            fenetre.blit(texte, (res[0] // 2 - 50, 10))
        
        pygame.display.update()
        Horloge.tick(fps_max)
        
        if statut_jeu in ["WIN", "LOSE"]:
            time.sleep(3)
            Sortie = True
    
    # Fermeture propre
    if reseau:
        reseau.fermer()
    pygame.quit()




def partie(params:Parametres=Parametres(joueurs=[Type_Joueur.HUMAIN],touches=[pygame.K_RIGHT,pygame.K_UP,pygame.K_LEFT,pygame.K_DOWN]),taille_laby=(10,10),mode_de_jeu="solo",
        ):
    """ boucle principale du jeu. Prend en argument les paramètre graphiques du style"""
    print("lancement d'une partie'")
    mode_de_jeu = "solo" if len(params.joueurs)==1 else "robot"
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
    if params.debug:
        Labyr.afficher_comme_texte()
    Labyr.visibles()

    if mode_de_jeu=="solo":
        Labyr.placer_depart(ratio_distance_min=0.7)
    elif mode_de_jeu=="robot":
        Labyr.placer_deux_joueurs(ratio_eloignement=0.6)

    joueurs = []

    for joueur_type in params.joueurs:

        if isinstance(joueur_type,Type_Joueur) :
            typ = joueur_type  
        else:
            typ = joueur_type[0]
        match typ:
            case Type_Joueur.HUMAIN:
                if mode_de_jeu=="solo":
                    # création du Joueur :
                    J1 = Joueur.Joueur(Labyr,Labyr.cases[Labyr.depart],(255,0,0),4,5)
                    J1.voir()
                    joueurs.append(J1)
                elif mode_de_jeu=="robot":
                    J1 = Joueur.Joueur(Labyr,Labyr.cases[Labyr.joueur1],(255,0,0),4,5)
                    J1.voir()
                    joueurs.append(J1)
            case Type_Joueur.ROBOT_ALEATOIRE:
                # mode_de_jeu = robot par défaut
                BOT = Joueur.Joueur(Labyr,Labyr.cases[Labyr.joueur2],(0,0,255),4,5,reflection="aleatoire")
                BOT.voir()
                if not isinstance(joueur_type,Type_Joueur):
                    BOT.asynchrone = True
                    BOT.moment_dernier_mvt = 0
                    BOT.mvt_par_sec = joueur_type[1]
                joueurs.append(BOT)
            case Type_Joueur.ROBOT_EXPLORATEUR:
                BOT = Joueur.Joueur(Labyr,Labyr.cases[Labyr.joueur2],(0,0,255),4,5,reflection="explorateur")
                BOT.voir()
                if not isinstance(joueur_type,Type_Joueur):
                    BOT.asynchrone = True
                    BOT.moment_dernier_mvt = 0
                    BOT.mvt_par_sec = joueur_type[1]
                joueurs.append(BOT)
    J1 = joueurs[0]
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
    Defaite = True
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
                J1.changement_direction(event.key,params.touches)
                J1.deplacement()
                J1.voir()

                if(J1.get_case_absolue() == Labyr.sortie):
                    print("Vous avez gagné !")
                    Defaiite = False
                    Sortie = True
                
                if len(joueurs)>1:
                    for i in range(1,len(joueurs)):
                        if not(joueurs[i].asynchrone):
                            # déplacement du robot
                            Affichage.effacer_joueur(fenetre,joueurs[i],min(res[0],res[1]),camera=type_vision)
                            
                            
                            joueurs[i].se_mouvoir()
                            joueurs[i].voir()
                            
                            if(joueurs[i].get_case_absolue() == Labyr.sortie):
                                print("Le robot a gagné ! Vous avez perdu.")
                                Sortie = True
                                Defaite = True

        for joueur in joueurs:
            if joueur.asynchrone:
                # gestion des déplacements asynchrones
                temps_actuel = pygame.time.get_ticks()
                intervalle_entre_mouvements = 1000 / joueur.mvt_par_sec  # en millisecondes
                if temps_actuel - joueur.moment_dernier_mvt >= intervalle_entre_mouvements:
                    # il est temps de faire un mouvement
                    Affichage.effacer_joueur(fenetre,joueur,min(res[0],res[1]),camera=type_vision)
                    joueur.se_mouvoir()
                    joueur.voir()
                    joueur.moment_dernier_mvt = temps_actuel

                    if(joueur.get_case_absolue() == Labyr.sortie):
                        if joueur == J1:# ne sert à rien pour l'instant
                            print("Vous avez gagné !")
                            Defaite = False
                        else:
                            print("Le robot a gagné ! Vous avez perdu.")
                            Defaite = True
                        Sortie = True
                    
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
        affiche_fenetre_fin(duree_totale/1000,victoire=False)
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
    """text_click = police_nationale.render("jeu Solo", 1, (0,0,0))
    rect_click = pygame.Rect(LARGEUR//2-largeur_rect//2,HAUTEUR//2-hauteur_rect//2,largeur_rect,hauteur_rect)
    """

    
    # affichage des éléments
    image = pygame.image.load("ressources/loading_image.png")
    image = pygame.transform.scale(image, res)

    # boucle principale menu :
    while True:
        for event in pygame.event.get():
            if (event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)
                    or (event.type == pygame.MOUSEBUTTONUP and rect_quit.collidepoint(pygame.mouse.get_pos()))):
                pygame.quit()
                sys.exit()
            
            # Gestion des clics sur les boutons
            if event.type == pygame.MOUSEBUTTONUP:
                # Bouton Jeu Solo
                if rect_click.collidepoint(pygame.mouse.get_pos()):
                    modeDeJeu = "solo"
                    j = [Type_Joueur.HUMAIN]
                    pygame.display.quit()
                    hauteur_defaut = 10
                    largeur_defaut = 10
                    hauteur_entree = affiche_fenetre_selection_valeur(texte="hauteur du labyrinthe : ",
                                                                      valeur_defaut=str(hauteur_defaut))
                    largeur_entree = affiche_fenetre_selection_valeur(texte="largeur du labyrinthe : ",
                                                                      valeur_defaut=str(largeur_defaut))

                    if largeur_entree == "":
                        largeur_entree = largeur_defaut
                    if hauteur_entree == "":
                        hauteur_entree = hauteur_defaut

                    partie(Parametres(joueurs=j, touches=[pygame.K_RIGHT, pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN]),
                           (int(largeur_entree), int(hauteur_entree)), mode_de_jeu=modeDeJeu)
                    pygame.quit()
                    sys.exit()
                
                # Bouton VS Robot
                elif rect_VS_robot.collidepoint(pygame.mouse.get_pos()):
                    modeDeJeu = "robot"
                    j = [Type_Joueur.HUMAIN, (Type_Joueur.ROBOT_EXPLORATEUR, 2.0)]
                    pygame.display.quit()
                    hauteur_defaut = 10
                    largeur_defaut = 10
                    hauteur_entree = affiche_fenetre_selection_valeur(texte="hauteur du labyrinthe : ",
                                                                      valeur_defaut=str(hauteur_defaut))
                    largeur_entree = affiche_fenetre_selection_valeur(texte="largeur du labyrinthe : ",
                                                                      valeur_defaut=str(largeur_defaut))

                    if largeur_entree == "":
                        largeur_entree = largeur_defaut
                    if hauteur_entree == "":
                        hauteur_entree = hauteur_defaut

                    partie(Parametres(joueurs=j, touches=[pygame.K_RIGHT, pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN]),
                           (int(largeur_entree), int(hauteur_entree)), mode_de_jeu=modeDeJeu)
                    pygame.quit()
                    sys.exit()
                
                # Bouton Héberger
                elif rect_heberger and rect_heberger.collidepoint(pygame.mouse.get_pos()):
                    pygame.display.quit()
                    heberger()
                    pygame.quit()
                    sys.exit()
                
                # Bouton Rejoindre
                elif rect_rejoindre and rect_rejoindre.collidepoint(pygame.mouse.get_pos()):
                    pygame.display.quit()
                    se_connecter()
                    pygame.quit()
                    sys.exit()
            
            # Gestion des touches clavier
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_s:
                    modeDeJeu = "solo"
                    j = [Type_Joueur.HUMAIN]
                    pygame.display.quit()
                    hauteur_defaut = 10
                    largeur_defaut = 10
                    hauteur_entree = affiche_fenetre_selection_valeur(texte="hauteur du labyrinthe : ",
                                                                      valeur_defaut=str(hauteur_defaut))
                    largeur_entree = affiche_fenetre_selection_valeur(texte="largeur du labyrinthe : ",
                                                                      valeur_defaut=str(largeur_defaut))

                    if largeur_entree == "":
                        largeur_entree = largeur_defaut
                    if hauteur_entree == "":
                        hauteur_entree = hauteur_defaut

                    partie(Parametres(joueurs=j, touches=[pygame.K_RIGHT, pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN]),
                           (int(largeur_entree), int(hauteur_entree)), mode_de_jeu=modeDeJeu)
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r:
                    modeDeJeu = "robot"
                    j = [Type_Joueur.HUMAIN, (Type_Joueur.ROBOT_EXPLORATEUR, 2.0)]
                    pygame.display.quit()
                    hauteur_defaut = 10
                    largeur_defaut = 10
                    hauteur_entree = affiche_fenetre_selection_valeur(texte="hauteur du labyrinthe : ",
                                                                      valeur_defaut=str(hauteur_defaut))
                    largeur_entree = affiche_fenetre_selection_valeur(texte="largeur du labyrinthe : ",
                                                                      valeur_defaut=str(largeur_defaut))

                    if largeur_entree == "":
                        largeur_entree = largeur_defaut
                    if hauteur_entree == "":
                        hauteur_entree = hauteur_defaut

                    partie(Parametres(joueurs=j, touches=[pygame.K_RIGHT, pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN]),
                           (int(largeur_entree), int(hauteur_entree)), mode_de_jeu=modeDeJeu)
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_h:  # H pour héberger
                    pygame.display.quit()
                    heberger()
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_j:  # J pour rejoindre
                    pygame.display.quit()
                    se_connecter()
                    pygame.quit()
                    sys.exit()

        # pygame.draw.rect(fenetre, (255, 255,255), rect_click)
        fenetre.blit(image, (0, 0))
        # affichage du rect (bouton sur lequel est ajouté text) :

        rect_click = Affichage.draw_text_box(fenetre, "Jeu Solo", police_nationale, LARGEUR // 2, HAUTEUR // 2,
                                             coul_bouton_clair)
        rect_VS_robot = Affichage.draw_text_box(fenetre, "Jeu VS Robot", police_nationale, LARGEUR // 2,
                                                HAUTEUR // 2 + dist_inter_rect + res[1] // 20, coul_bouton_clair)
        rect_heberger = Affichage.draw_text_box(fenetre, "Héberger", police_nationale, LARGEUR // 2,
                                                HAUTEUR // 2 + 2 * (dist_inter_rect + res[1] // 20), coul_bouton_clair)
        rect_rejoindre = Affichage.draw_text_box(fenetre, "Rejoindre", police_nationale, LARGEUR // 2,
                                                 HAUTEUR // 2 + 3 * (dist_inter_rect + res[1] // 20), coul_bouton_clair)
        rect_quit = Affichage.draw_text_box(fenetre, "Quitter", police_nationale, LARGEUR // 2,
                                            HAUTEUR // 2 + 4 * (dist_inter_rect + res[1] // 20), coul_bouton_clair)

        
        
        pygame.display.flip()
        Horloge.tick(60)



    pygame.init()
    print("fin du programme")
