#import Laby
from Laby import *
import global_data
import Affichage
from Affichage import Camera
import sys 
import pygame
import Joueur
from Network import Network
import socket
import threading
import server as server_module # On importe notre fichier server.py

pygame.init()

# --- COULEURS POUR LES JOUEURS (Jusqu'à 6, puis ça boucle) ---
COULEURS_JOUEURS = [
    (255, 0, 0),    # J1: Rouge
    (0, 0, 255),    # J2: Bleu
    (0, 200, 0),    # J3: Vert
    (255, 255, 0),  # J4: Jaune
    (255, 0, 255),  # J5: Magenta
    (0, 255, 255)   # J6: Cyan
]

# --- UTILITAIRES ---
def get_local_ip():
    """Tente de trouver l'IP locale utilisée pour se connecter à internet"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # On n'a pas besoin d'être connecté à internet, mais cela force l'OS
        # à choisir la bonne interface réseau (Wifi ou Ethernet)
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

# --- FENETRES SECONDAIRES ---

def affiche_fenetre_saisie_ip(texte_titre="Entrez l'IP du serveur"):
    fen1 = pygame.display.set_mode((750, 600))
    valeur = ""
    active = True
    clock = pygame.time.Clock()
    
    # Tentative chargement image fond
    try:
        image = pygame.image.load("ressources/loading_image.png")
        image = pygame.transform.scale(image, (750, 600))
    except: image = None

    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: active = False
                elif event.key == pygame.K_BACKSPACE: valeur = valeur[:-1]
                elif event.key == pygame.K_ESCAPE: return None
                else: valeur += event.unicode

        if image: fen1.blit(image, (0,0))
        else: fen1.fill((255,255,255))

        police = pygame.font.SysFont('Corbel', 50)
        txt_titre = police.render(texte_titre, True, (0,0,0))
        fen1.blit(txt_titre, (375 - txt_titre.get_width()//2, 200))
        
        # Zone de saisie
        rect_saisie = pygame.Rect(375 - 200, 300, 400, 60)
        pygame.draw.rect(fen1, (200,240,200), rect_saisie)
        
        txt_val = police.render(valeur if valeur else "IP...", True, (0,0,0) if valeur else (100,100,100))
        fen1.blit(txt_val, (rect_saisie.centerx - txt_val.get_width()//2, rect_saisie.centery - txt_val.get_height()//2))
        
        pygame.display.update()
        clock.tick(30)
    return valeur if valeur != "" else "localhost"

def affiche_fenetre_nb_joueurs():
    """Demande le nombre de joueurs pour le serveur (2 à 9)"""
    fen = pygame.display.set_mode((750, 600))
    valeur = ""
    active = True
    
    try:
        image = pygame.image.load("ressources/loading_image.png")
        image = pygame.transform.scale(image, (750, 600))
    except: image = None

    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: 
                    if valeur.isdigit() and int(valeur) >= 2: return int(valeur)
                elif event.key == pygame.K_ESCAPE: return None
                elif event.unicode.isdigit(): 
                    valeur = event.unicode # On ne garde qu'un chiffre
        
        if image: fen.blit(image, (0,0))
        else: fen.fill((255,255,255))
        
        font = pygame.font.SysFont('Corbel', 50)
        txt = font.render(f"Nombre de joueurs ? (2-9)", True, (0,0,0))
        fen.blit(txt, (375 - txt.get_width()//2, 250))
        
        rect_saisie = pygame.Rect(375 - 50, 320, 100, 60)
        pygame.draw.rect(fen, (200,240,200), rect_saisie)
        
        txt_val = font.render(valeur, True, (0,0,0))
        fen.blit(txt_val, (rect_saisie.centerx - txt_val.get_width()//2, rect_saisie.centery - txt_val.get_height()//2))

        pygame.display.update()
    return 2

def affiche_fenetre_victoire(nb_ticks):
    res = (620,220); fenetre = pygame.display.set_mode(res)
    police = pygame.font.SysFont('Corbel',res[1]//10) 
    texte = police.render("Victoire en "+str(round(nb_ticks, 2))+" s !" , True , (0,0,0))
    fenetre.fill((255, 255,255)); fenetre.blit(texte, (res[0]//10, res[1]//2 - res[1]//10))
    pygame.display.update(); pygame.time.delay(3000)

def affiche_fenetre_defaite():
    res = (620,220); fenetre = pygame.display.set_mode(res)
    police = pygame.font.SysFont('Corbel',res[1]//5)
    texte = police.render("Perdu ! Un autre a gagné.", True , (200,0,0))
    fenetre.fill((255, 255,255)); fenetre.blit(texte, (res[0]//10, res[1]//2 - res[1]//10))
    pygame.display.update(); pygame.time.delay(3000)

# --- CŒUR DU JEU ---

def partie(taille_laby=(10,10), mode_de_jeu="solo", ip_serveur="localhost",
        coul_fond=(255,255,255), debug=False):
    
    pygame.init() 
    res = (720,720)
    fenetre = pygame.display.set_mode(res)
    pygame.display.set_caption("Jeu de labyrinthe")
    Horloge = pygame.time.Clock()
    fps_max = 60
    
    joueurs = [] # Liste contenant TOUS les objets Joueur
    mon_id = 0
    reseau = None
    J_Moi = None
    
    # Nombre de joueurs total (par défaut 1 en solo, N en réseau)
    nb_total_joueurs = 1 

    # --- INITIALISATION SELON LE MODE ---
    if mode_de_jeu == "reseau":
        # Ecran de chargement
        fenetre.fill((255,255,255))
        police = pygame.font.SysFont('Corbel',30)
        txt = police.render(f"Connexion à {ip_serveur}...", True, (0,0,0))
        fenetre.blit(txt, (res[0]//2 - txt.get_width()//2, res[1]//2))
        pygame.display.update()

        reseau = Network(ip_serveur)
        if reseau.p is None:
            return # Echec connexion, retour menu

        # On récupère : Le Labyrinthe, Mon ID, Le Nombre Total de Joueurs
        Labyr, mon_id, nb_total_joueurs = reseau.p
        Labyr.visibles()
        
        # Création de TOUS les joueurs (liste)
        for i in range(nb_total_joueurs):
            # On récupère la case de départ prévue par le serveur pour le joueur i
            # Le serveur a stocké les indices de départ dans Labyr.joueurs_indices
            idx_case_depart = Labyr.joueurs_indices[i]
            
            # Couleur cyclique
            couleur = COULEURS_JOUEURS[i % len(COULEURS_JOUEURS)]
            
            # Création du joueur
            nouveau_joueur = Joueur.Joueur(Labyr, Labyr.cases[idx_case_depart], couleur, 4, 5)
            joueurs.append(nouveau_joueur)
            
            # Est-ce moi ?
            if i == mon_id:
                J_Moi = nouveau_joueur
        
        # Initialisation vue
        J_Moi.voir()
        largeur = Labyr.largeur
        hauteur = Labyr.hauteur

    else:
        # MODE SOLO OU ROBOT (Logiciel local)
        largeur = taille_laby[1]
        hauteur = taille_laby[0]
        Labyr = Labyrinthe(largeur,hauteur)
        Labyr.generer_par_Wilson()
        Labyr.visibles()

        if mode_de_jeu=="solo":
            Labyr.placer_depart(ratio_distance_min=0.7)
            J_Moi = Joueur.Joueur(Labyr,Labyr.cases[Labyr.depart],(255,0,0),4,5)
            J_Moi.voir()
            joueurs.append(J_Moi)
        
        if mode_de_jeu=="robot":
            Labyr.placer_deux_joueurs(ratio_eloignement=0.6)
            J_Moi = Joueur.Joueur(Labyr,Labyr.cases[Labyr.joueur1],(255,0,0),4,5)
            J_Moi.voir()
            joueurs.append(J_Moi)
            # Le robot
            BOT = Joueur.Joueur(Labyr,Labyr.cases[Labyr.joueur2],(0,0,255),4,5)
            joueurs.append(BOT)

    # --- CAMÉRA ---
    type_vision = Camera()
    type_vision.centrage = J_Moi
    
    if mode_de_jeu == "reseau":
        type_vision.hauteur_vision = 12
        type_vision.largeur_vision = 12
    else:
        type_vision.hauteur_vision = min(hauteur, largeur)
        type_vision.largeur_vision = min(hauteur, largeur)

    # --- BOUCLE DE JEU ---
    Sortie = False
    Defaite = False
    duree_totale = 0
    touches = [pygame.K_z, pygame.K_q, pygame.K_s, pygame.K_d]

    while not Sortie:
        can_move = True
        
        # 1. GESTION RESEAU
        if mode_de_jeu == "reseau":
            try:
                # J'envoie ma position -> Je reçois (Liste_Des_Positions, Status)
                reponse = reseau.send(J_Moi.get_case_absolue())
                
                if reponse:
                    positions_tous, GameStatus = reponse
                    
                    # Mise à jour des autres joueurs
                    for i in range(len(joueurs)):
                        if i != mon_id: # On ne se met pas à jour soi-même (évite le lag visuel)
                            # positions_tous est une liste [posJ0, posJ1, posJ2...]
                            if i < len(positions_tous):
                                joueurs[i].set_case_absolue(positions_tous[i])

                    if GameStatus == "WAIT":
                        can_move = False
                    elif GameStatus == "WIN":
                        Sortie = True
                        Defaite = False
                    elif GameStatus == "LOSE":
                        Sortie = True
                        Defaite = True
                else:
                    print("Perte connexion serveur")
                    Sortie = True
            except Exception as e:
                print("Erreur boucle réseau:", e)
                Sortie = True

        # 2. EVENEMENTS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Sortie = True
                Defaite = True
            
            if event.type == pygame.KEYDOWN and can_move:
                Affichage.effacer_joueur(fenetre, J_Moi, min(res[0],res[1]), camera=type_vision)
                J_Moi.changement_direction(event.key, touches)
                J_Moi.deplacement()
                J_Moi.voir()

                # Victoire Solo / Robot Locale
                if mode_de_jeu != "reseau" and J_Moi.get_case_absolue() == Labyr.sortie:
                    Sortie = True
                    Defaite = False

        # 3. AFFICHAGE
        Affichage.tout_effacer(fenetre)

        if mode_de_jeu == "reseau" and not can_move:
            # Ecran d'attente
            police_att = pygame.font.SysFont('Corbel', 40)
            txt = police_att.render("En attente des autres joueurs...", True, (0,0,0))
            fenetre.blit(txt, (res[0]//2 - txt.get_width()//2, res[1]//2))
        else:
            # Affichage du jeu
            Affichage.affiche_ensemble_de_cases(fenetre,Labyr,J_Moi.cases_vues,min(res[0],res[1]),coul_mur=(150,150,150),camera=type_vision)
            Affichage.affiche_ensemble_de_cases(fenetre,Labyr,J_Moi.visu_actuel,min(res[0],res[1]),coul_mur=(0,0,0),camera=type_vision)
            
            # Afficher TOUS les joueurs
            for j in joueurs:
                Affichage.afficher_joueur(fenetre, j, min(res[0],res[1]), camera=type_vision)

        pygame.display.update()
        Horloge.tick(fps_max)
        if can_move:
            duree_totale += Horloge.get_time()

    # 4. FIN DE PARTIE
    if mode_de_jeu == "reseau":
        reseau.close()
    
    if not Defaite:
        affiche_fenetre_victoire(duree_totale/1000)
    elif mode_de_jeu == "reseau":
        affiche_fenetre_defaite()

# --- MENU PRINCIPAL ---
if __name__=="__main__":
    pygame.init() 
    HAUTEUR = 600
    LARGEUR = 750
    res = (LARGEUR,HAUTEUR) 
    fenetre = pygame.display.set_mode(res)
    Horloge = pygame.time.Clock()

    # Style
    coul_bouton_clair = (200,240,200)
    coul_bouton_reseau = (200,220,255) # Bleu clair pour le réseau
    coul_bouton_rouge = (255,200,200) # Pour fermer le serveur

    # Chargement Image
    try:
        image_fond = pygame.image.load("ressources/loading_image.png")
        image_fond = pygame.transform.scale(image_fond, res)
    except:
        image_fond = None

    # Dimensions Boutons
    largeur_btn = 250
    hauteur_btn = 60
    espacement = 20
    start_y = 130
    x_center = LARGEUR//2 - largeur_btn//2
    
    # Création des Rects pour les clics
    rect_solo = pygame.Rect(x_center, start_y, largeur_btn, hauteur_btn)
    rect_robot = pygame.Rect(x_center, start_y + 1*(hauteur_btn+espacement), largeur_btn, hauteur_btn)
    rect_host = pygame.Rect(x_center, start_y + 2*(hauteur_btn+espacement), largeur_btn, hauteur_btn)
    rect_join = pygame.Rect(x_center, start_y + 3*(hauteur_btn+espacement), largeur_btn, hauteur_btn)
    rect_quit = pygame.Rect(x_center, start_y + 4*(hauteur_btn+espacement), largeur_btn, hauteur_btn)

    police_corbel = pygame.font.SysFont('Corbel', 45)

    mode_host_actif = False
    server_thread = None
    local_ip = get_local_ip()

    while True:
        pos_souris = pygame.mouse.get_pos()
        
        if not mode_host_actif:
            # --- MENU NORMAL ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                
                if event.type == pygame.MOUSEBUTTONUP:
                    if rect_solo.collidepoint(pos_souris):
                        partie((15,15), "solo")
                        fenetre = pygame.display.set_mode(res)
                    elif rect_robot.collidepoint(pos_souris):
                        partie((15,15), "robot")
                        fenetre = pygame.display.set_mode(res)
                    
                    elif rect_host.collidepoint(pos_souris):
                        # 1. Demander le nombre de joueurs
                        nb = affiche_fenetre_nb_joueurs()
                        if nb and nb >= 2:
                            # 2. Démarrer le serveur avec ce nombre
                            if server_thread is None or not server_thread.is_alive():
                                server_thread = threading.Thread(target=server_module.run_server, args=(nb,))
                                server_thread.daemon = True
                                server_thread.start()
                            mode_host_actif = True
                        # Sinon (Annulation), on ne fait rien
                        fenetre = pygame.display.set_mode(res)

                    elif rect_join.collidepoint(pos_souris):
                        ip = affiche_fenetre_saisie_ip()
                        if ip:
                            partie((10,10), "reseau", ip_serveur=ip)
                            fenetre = pygame.display.set_mode(res)
                    
                    elif rect_quit.collidepoint(pos_souris):
                        if server_thread: server_module.stop_server()
                        pygame.quit(); sys.exit()

            # Dessin Menu Normal
            if image_fond: fenetre.blit(image_fond, (0, 0))
            else: fenetre.fill((255,255,255))
            
            boutons = [
                (rect_solo, "Solo", coul_bouton_clair),
                (rect_robot, "VS Robot", coul_bouton_clair),
                (rect_host, "Héberger", coul_bouton_reseau),
                (rect_join, "Rejoindre", coul_bouton_reseau),
                (rect_quit, "Quitter", coul_bouton_clair)
            ]
            
            for rect, texte, couleur in boutons:
                pygame.draw.rect(fenetre, couleur, rect)
                txt_surf = police_corbel.render(texte, True, (0,0,0))
                fenetre.blit(txt_surf, (rect.centerx - txt_surf.get_width()//2, rect.centery - txt_surf.get_height()//2))

        else:
            # --- MENU MODE HÉBERGEMENT (HOST) ---
            # Boutons spécifiques à cet écran
            rect_join_local = pygame.Rect(x_center, start_y + 2*(hauteur_btn+espacement), largeur_btn, hauteur_btn)
            rect_stop_server = pygame.Rect(x_center, start_y + 3*(hauteur_btn+espacement), largeur_btn, hauteur_btn)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    server_module.stop_server()
                    pygame.quit(); sys.exit()
                
                if event.type == pygame.MOUSEBUTTONUP:
                    if rect_join_local.collidepoint(pos_souris):
                        # L'hôte rejoint sa propre partie
                        partie((10,10), "reseau", ip_serveur="localhost")
                        fenetre = pygame.display.set_mode(res)
                    
                    elif rect_stop_server.collidepoint(pos_souris):
                        # On arrête le serveur et on revient au menu
                        server_module.stop_server()
                        mode_host_actif = False

            # Dessin Menu Host
            if image_fond: fenetre.blit(image_fond, (0, 0))
            else: fenetre.fill((255,255,255))
            
            # Affichage de l'IP
            police_titre = pygame.font.SysFont('Corbel', 40)
            txt_info = police_titre.render("Serveur en ligne !", True, (0,100,0))
            fenetre.blit(txt_info, (LARGEUR//2 - txt_info.get_width()//2, 100))
            
            # Boite affichant l'IP
            rect_ip = pygame.Rect(LARGEUR//2 - 200, 160, 400, 60)
            pygame.draw.rect(fenetre, (255,255,255), rect_ip)
            pygame.draw.rect(fenetre, (0,0,0), rect_ip, 3) # Bordure noire
            
            txt_ip = police_corbel.render(f"IP: {local_ip}", True, (0,0,0))
            fenetre.blit(txt_ip, (rect_ip.centerx - txt_ip.get_width()//2, rect_ip.centery - txt_ip.get_height()//2))
            
            # Boutons
            pygame.draw.rect(fenetre, coul_bouton_reseau, rect_join_local)
            txt_j = police_corbel.render("Jouer (Hôte)", True, (0,0,0))
            fenetre.blit(txt_j, (rect_join_local.centerx - txt_j.get_width()//2, rect_join_local.centery - txt_j.get_height()//2))
            
            pygame.draw.rect(fenetre, coul_bouton_rouge, rect_stop_server)
            txt_s = police_corbel.render("Arrêter Serveur", True, (0,0,0))
            fenetre.blit(txt_s, (rect_stop_server.centerx - txt_s.get_width()//2, rect_stop_server.centery - txt_s.get_height()//2))

        pygame.display.flip()
        Horloge.tick(60)