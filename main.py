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
import server as server_module

pygame.init()

# --- COULEURS ---
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
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def dessiner_texte_avec_fond(surface, texte, font, x, y, couleur_texte=(0,0,0), couleur_fond=(255,255,255), padding=10):
    """Fonction utilitaire pour dessiner du texte lisible sur n'importe quel fond"""
    surf_texte = font.render(texte, True, couleur_texte)
    rect_texte = surf_texte.get_rect(center=(x, y))
    # Dessin du rectangle de fond
    rect_fond = rect_texte.inflate(padding*2, padding*2)
    pygame.draw.rect(surface, couleur_fond, rect_fond, border_radius=5)
    # Dessin du bord noir autour du fond (optionnel, pour faire propre)
    pygame.draw.rect(surface, (0,0,0), rect_fond, 2, border_radius=5)
    # Dessin du texte
    surface.blit(surf_texte, rect_texte)

# --- FENETRES SECONDAIRES ---

def affiche_fenetre_saisie_ip(historique_ips=[], texte_titre="Entrez l'IP du serveur"):
    fen1 = pygame.display.set_mode((750, 600))
    valeur = ""
    active = True
    clock = pygame.time.Clock()
    
    try:
        image = pygame.image.load("ressources/loading_image.png")
        image = pygame.transform.scale(image, (750, 600))
    except: image = None

    font_titre = pygame.font.SysFont('Corbel', 50)
    font_hist = pygame.font.SysFont('Corbel', 35)

    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return None
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: active = False
                elif event.key == pygame.K_BACKSPACE: valeur = valeur[:-1]
                elif event.key == pygame.K_ESCAPE: return None
                else: valeur += event.unicode
            
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                start_y_hist = 400
                for i, ip_saved in enumerate(historique_ips):
                    rect_hist = pygame.Rect(375 - 150, start_y_hist + i*40, 300, 35)
                    if rect_hist.collidepoint(pos):
                        valeur = ip_saved
                        active = False

        if image: fen1.blit(image, (0,0))
        else: fen1.fill((255,255,255))

        # Utilisation de la nouvelle fonction avec fond
        dessiner_texte_avec_fond(fen1, texte_titre, font_titre, 375, 150)
        
        # Zone de saisie
        rect_saisie = pygame.Rect(375 - 200, 250, 400, 60)
        pygame.draw.rect(fen1, (200,240,200), rect_saisie)
        pygame.draw.rect(fen1, (0,0,0), rect_saisie, 2) # Bordure
        
        txt_val = font_titre.render(valeur if valeur else "IP...", True, (0,0,0) if valeur else (100,100,100))
        fen1.blit(txt_val, (rect_saisie.centerx - txt_val.get_width()//2, rect_saisie.centery - txt_val.get_height()//2))
        
        if historique_ips:
            dessiner_texte_avec_fond(fen1, "Récents :", font_hist, 375, 360, padding=5)
            
            start_y_hist = 400
            for i, ip_saved in enumerate(historique_ips):
                if i >= 4: break
                rect_hist = pygame.Rect(375 - 150, start_y_hist + i*45, 300, 40)
                col = (220, 220, 255) if rect_hist.collidepoint(pygame.mouse.get_pos()) else (240, 240, 240)
                pygame.draw.rect(fen1, col, rect_hist, border_radius=10)
                pygame.draw.rect(fen1, (0,0,0), rect_hist, 1, border_radius=10)
                
                txt_ip = font_hist.render(ip_saved, True, (0,0,0))
                fen1.blit(txt_ip, (rect_hist.centerx - txt_ip.get_width()//2, rect_hist.centery - txt_ip.get_height()//2))

        dessiner_texte_avec_fond(fen1, "Échap pour annuler", pygame.font.SysFont('Corbel', 25), 100, 30)

        pygame.display.update()
        clock.tick(30)
    return valeur if valeur != "" else "localhost"

def affiche_fenetre_nb_joueurs():
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
                elif event.unicode.isdigit(): valeur = event.unicode 
        
        if image: fen.blit(image, (0,0))
        else: fen.fill((255,255,255))
        
        font = pygame.font.SysFont('Corbel', 50)
        dessiner_texte_avec_fond(fen, "Nombre de joueurs ? (2-9)", font, 375, 250)
        
        rect_saisie = pygame.Rect(375 - 50, 320, 100, 60)
        pygame.draw.rect(fen, (200,240,200), rect_saisie)
        pygame.draw.rect(fen, (0,0,0), rect_saisie, 2)
        
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
        coul_fond=(255,255,255), debug=False, niveau_robot_intelligent=False, vitesse_bot=250):
    
    pygame.init() 
    res = (720,720)
    fenetre = pygame.display.set_mode(res)
    pygame.display.set_caption("Jeu de labyrinthe")
    Horloge = pygame.time.Clock()
    fps_max = 60
    
    joueurs = []
    mon_id = 0
    reseau = None
    J_Moi = None
    nb_total_joueurs = 1 

    # --- INITIALISATION ---
    if mode_de_jeu == "reseau":
        fenetre.fill((255,255,255))
        police = pygame.font.SysFont('Corbel',30)
        dessiner_texte_avec_fond(fenetre, f"Connexion à {ip_serveur}...", police, res[0]//2, res[1]//2)
        pygame.display.update()

        reseau = Network(ip_serveur)
        if reseau.p is None: return

        Labyr, mon_id, nb_total_joueurs = reseau.p
        Labyr.visibles()
        
        for i in range(nb_total_joueurs):
            idx_case_depart = Labyr.joueurs_indices[i]
            couleur = COULEURS_JOUEURS[i % len(COULEURS_JOUEURS)]
            nouveau_joueur = Joueur.Joueur(Labyr, Labyr.cases[idx_case_depart], couleur, 4, 5)
            joueurs.append(nouveau_joueur)
            if i == mon_id: J_Moi = nouveau_joueur
        
        J_Moi.voir()
        largeur = Labyr.largeur; hauteur = Labyr.hauteur

    else:
        # MODE SOLO/ROBOT
        largeur = taille_laby[1]; hauteur = taille_laby[0]
        Labyr = Labyrinthe(largeur,hauteur)
        Labyr.generer_par_Wilson()
        Labyr.visibles()
        Labyr.cases[Labyr.sortie].contenu = "Sortie"

        if mode_de_jeu=="solo":
            Labyr.placer_depart(ratio_distance_min=0.7)
            J_Moi = Joueur.Joueur(Labyr,Labyr.cases[Labyr.depart],(255,0,0),4,5)
            J_Moi.voir(); joueurs.append(J_Moi)
        
        if mode_de_jeu=="robot":
            Labyr.placer_deux_joueurs(ratio_eloignement=0.6)
            J_Moi = Joueur.Joueur(Labyr,Labyr.cases[Labyr.joueur1],(255,0,0),4,5)
            J_Moi.voir(); joueurs.append(J_Moi)
            # Le robot est ajouté
            BOT = Joueur.Joueur(Labyr,Labyr.cases[Labyr.joueur2],(0,0,255),4,5)
            joueurs.append(BOT)

    # --- CAMÉRA ---
    type_vision = Camera()
    type_vision.centrage = J_Moi
    if mode_de_jeu == "reseau":
        type_vision.hauteur_vision = 12; type_vision.largeur_vision = 12
    else:
        type_vision.hauteur_vision = min(hauteur, largeur); type_vision.largeur_vision = min(hauteur, largeur)

    Sortie = False
    Defaite = False
    duree_totale = 0
    touches = [pygame.K_z, pygame.K_q, pygame.K_s, pygame.K_d]

    # IP pour affichage attente
    ip_affichage = ip_serveur
    if ip_serveur == "localhost" or ip_serveur == "127.0.0.1":
        ip_affichage = get_local_ip()
    
    dernier_move_robot = 0

    while not Sortie:
        can_move = True
        temps_actuel = pygame.time.get_ticks() # Récupérer le temps actuel

        # --- GESTION DU ROBOT ---
        if mode_de_jeu == "robot" and not Defaite:
            # On utilise vitesse_bot ici
            if temps_actuel - dernier_move_robot > vitesse_bot:
                
                # On passe niveau_robot_intelligent à la méthode (qui sera True dans les 2 cas maintenant)
                BOT.bot_move(intelligent=niveau_robot_intelligent) 
                
                dernier_move_robot = temps_actuel
                
                if BOT.get_case_absolue() == Labyr.sortie:
                    affiche_fenetre_defaite()
                    Sortie = True
        
        # 1. GESTION RESEAU
        if mode_de_jeu == "reseau":
            try:
                reponse = reseau.send(J_Moi.get_case_absolue())
                if reponse:
                    positions_tous, GameStatus = reponse
                    for i in range(len(joueurs)):
                        if i != mon_id and i < len(positions_tous):
                            joueurs[i].set_case_absolue(positions_tous[i])

                    if GameStatus == "WAIT": can_move = False
                    elif GameStatus == "WIN": Sortie = True; Defaite = False
                    elif GameStatus == "LOSE": Sortie = True; Defaite = True
                else: Sortie = True
            except Exception as e: Sortie = True

        # 2. EVENEMENTS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Sortie = True
                Defaite = True
            
            # --- MODIFICATION CLÉ POUR ÉCHAP ---
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    Sortie = True
                    if mode_de_jeu == "reseau" and not can_move:
                        # Si on est en attente, ce n'est PAS une défaite, juste un départ
                        Defaite = False 
                    else:
                        # Si on est en jeu, c'est un abandon
                        Defaite = True 
                
                elif can_move:
                    Affichage.effacer_joueur(fenetre, J_Moi, min(res[0],res[1]), camera=type_vision)
                    J_Moi.changement_direction(event.key, touches)
                    J_Moi.deplacement()
                    J_Moi.voir()
                    if mode_de_jeu != "reseau" and J_Moi.get_case_absolue() == Labyr.sortie:
                        Sortie = True; Defaite = False

        # 3. AFFICHAGE
        Affichage.tout_effacer(fenetre)

        if mode_de_jeu == "reseau" and not can_move:
            # --- MODIFICATION CLÉ POUR LISIBILITÉ ---
            police_att = pygame.font.SysFont('Corbel', 40)
            police_ip = pygame.font.SysFont('Corbel', 30)
            police_esc = pygame.font.SysFont('Corbel', 25)
            
            dessiner_texte_avec_fond(fenetre, "En attente de joueurs...", police_att, res[0]//2, res[1]//2 - 50)
            dessiner_texte_avec_fond(fenetre, f"IP de la partie : {ip_affichage}", police_ip, res[0]//2, res[1]//2 + 20)
            dessiner_texte_avec_fond(fenetre, "(Échap pour quitter la file)", police_esc, res[0]//2, res[1]//2 + 70)

        else:
            Affichage.affiche_ensemble_de_cases(fenetre,Labyr,J_Moi.cases_vues,min(res[0],res[1]),coul_mur=(150,150,150),camera=type_vision)
            Affichage.affiche_ensemble_de_cases(fenetre,Labyr,J_Moi.visu_actuel,min(res[0],res[1]),coul_mur=(0,0,0),camera=type_vision)
            for j in joueurs:
                Affichage.afficher_joueur(fenetre, j, min(res[0],res[1]), camera=type_vision)

        pygame.display.update()
        Horloge.tick(fps_max)
        if can_move: duree_totale += Horloge.get_time()

    if mode_de_jeu == "reseau": reseau.close()
    
    # On n'affiche la défaite que si Defaite est True
    if not Defaite:
        # Si on a gagné ou si on a quitté proprement la file, on ne met rien ou victoire
        if can_move: # Si on a joué un peu (victoire)
            affiche_fenetre_victoire(duree_totale/1000)
        # Sinon (quitté file), on retourne juste au menu sans rien afficher
    elif mode_de_jeu == "reseau":
        affiche_fenetre_defaite()

# --- MENU PRINCIPAL ---
if __name__=="__main__":
    pygame.init() 
    HAUTEUR = 600; LARGEUR = 750
    res = (LARGEUR,HAUTEUR) 
    fenetre = pygame.display.set_mode(res)
    Horloge = pygame.time.Clock()

    historique_ips = []
    coul_bouton_clair = (200,240,200)
    coul_bouton_reseau = (200,220,255)
    coul_bouton_rouge = (255,200,200)

    try:
        image_fond = pygame.image.load("ressources/loading_image.png")
        image_fond = pygame.transform.scale(image_fond, res)
    except: image_fond = None

    largeur_btn = 250; hauteur_btn = 60; espacement = 20; start_y = 130
    x_center = LARGEUR//2 - largeur_btn//2
    
    rect_solo = pygame.Rect(x_center, start_y, largeur_btn, hauteur_btn)
    largeur_demi = (largeur_btn - 10) // 2
    rect_robot_facile = pygame.Rect(x_center, start_y + 1*(hauteur_btn+espacement), largeur_demi, hauteur_btn)
    rect_robot_malin = pygame.Rect(x_center + largeur_demi + 10, start_y + 1*(hauteur_btn+espacement), largeur_demi, hauteur_btn)
    rect_host = pygame.Rect(x_center, start_y + 2*(hauteur_btn+espacement), largeur_btn, hauteur_btn)
    rect_join = pygame.Rect(x_center, start_y + 3*(hauteur_btn+espacement), largeur_btn, hauteur_btn)
    rect_quit = pygame.Rect(x_center, start_y + 4*(hauteur_btn+espacement), largeur_btn, hauteur_btn)

    police_corbel = pygame.font.SysFont('Corbel', 45)
    police_petite = pygame.font.SysFont('Corbel', 30)

    mode_host_actif = False
    server_thread = None
    local_ip = get_local_ip()

    while True:
        pos_souris = pygame.mouse.get_pos()
        
        if not mode_host_actif:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    if rect_solo.collidepoint(pos_souris):
                        partie((15,15), "solo"); fenetre = pygame.display.set_mode(res)
                    elif rect_robot_facile.collidepoint(pos_souris):
                        # On lance en mode robot avec intelligent=False
                        partie((15,15), "robot", niveau_robot_intelligent=True, vitesse_bot=500)
                        fenetre = pygame.display.set_mode(res)
                    elif rect_robot_malin.collidepoint(pos_souris):
                        # On lance en mode robot avec intelligent=True
                        partie((15,15), "robot", niveau_robot_intelligent=True, vitesse_bot=250)
                        fenetre = pygame.display.set_mode(res)
                    
                    elif rect_host.collidepoint(pos_souris):
                        nb = affiche_fenetre_nb_joueurs()
                        if nb and nb >= 2:
                            if server_thread is None or not server_thread.is_alive():
                                server_thread = threading.Thread(target=server_module.run_server, args=(nb,))
                                server_thread.daemon = True
                                server_thread.start()
                            mode_host_actif = True
                        fenetre = pygame.display.set_mode(res)

                    elif rect_join.collidepoint(pos_souris):
                        ip = affiche_fenetre_saisie_ip(historique_ips)
                        if ip:
                            if ip not in historique_ips and ip != "localhost":
                                historique_ips.insert(0, ip)
                            partie((10,10), "reseau", ip_serveur=ip)
                            fenetre = pygame.display.set_mode(res)
                    
                    elif rect_quit.collidepoint(pos_souris):
                        if server_thread: server_module.stop_server()
                        pygame.quit(); sys.exit()

            if image_fond: fenetre.blit(image_fond, (0, 0))
            else: fenetre.fill((255,255,255))
            
            # Solo
            pygame.draw.rect(fenetre, coul_bouton_clair, rect_solo)
            txt_s = police_corbel.render("Solo", True, (0,0,0))
            fenetre.blit(txt_s, (rect_solo.centerx - txt_s.get_width()//2, rect_solo.centery - txt_s.get_height()//2))

            # --- DESSIN DES DEUX BOUTONS ROBOT ---
            pygame.draw.rect(fenetre, (255,255,220), rect_robot_facile) # Vert clair
            txt_rf = police_petite.render("Bot facile", True, (0,0,0))
            fenetre.blit(txt_rf, (rect_robot_facile.centerx - txt_rf.get_width()//2, rect_robot_facile.centery - txt_rf.get_height()//2))

            pygame.draw.rect(fenetre, (255,220,220), rect_robot_malin) # Rouge clair
            txt_rm = police_petite.render("Bot difficile", True, (0,0,0))
            fenetre.blit(txt_rm, (rect_robot_malin.centerx - txt_rm.get_width()//2, rect_robot_malin.centery - txt_rm.get_height()//2))
            # -------------------------------------

            # Host, Join, Quit
            boutons_standard = [
                (rect_host, "Héberger", coul_bouton_reseau),
                (rect_join, "Rejoindre", coul_bouton_reseau),
                (rect_quit, "Quitter", (255, 120, 120))
            ]
            for rect, texte, couleur in boutons_standard:
                pygame.draw.rect(fenetre, couleur, rect)
                txt_surf = police_corbel.render(texte, True, (0,0,0))
                fenetre.blit(txt_surf, (rect.centerx - txt_surf.get_width()//2, rect.centery - txt_surf.get_height()//2))

        else:
            # MODE HOST
            rect_join_local = pygame.Rect(x_center, start_y + 2*(hauteur_btn+espacement), largeur_btn, hauteur_btn)
            rect_stop_server = pygame.Rect(x_center, start_y + 3*(hauteur_btn+espacement), largeur_btn, hauteur_btn)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    server_module.stop_server(); pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    if rect_join_local.collidepoint(pos_souris):
                        partie((10,10), "reseau", ip_serveur="localhost")
                        fenetre = pygame.display.set_mode(res)
                    elif rect_stop_server.collidepoint(pos_souris):
                        server_module.stop_server(); mode_host_actif = False

            if image_fond: fenetre.blit(image_fond, (0, 0))
            else: fenetre.fill((255,255,255))
            
            police_titre = pygame.font.SysFont('Corbel', 40)
            dessiner_texte_avec_fond(fenetre, "Serveur en ligne !", police_titre, LARGEUR//2, 100)
            
            # Affichage IP (Fond manuel pour le style rectangle)
            rect_ip = pygame.Rect(LARGEUR//2 - 200, 160, 400, 60)
            pygame.draw.rect(fenetre, (255,255,255), rect_ip)
            pygame.draw.rect(fenetre, (0,0,0), rect_ip, 3)
            txt_ip = police_corbel.render(f"IP: {local_ip}", True, (0,0,0))
            fenetre.blit(txt_ip, (rect_ip.centerx - txt_ip.get_width()//2, rect_ip.centery - txt_ip.get_height()//2))
            
            pygame.draw.rect(fenetre, coul_bouton_reseau, rect_join_local)
            txt_j = police_corbel.render("Jouer (Hôte)", True, (0,0,0))
            fenetre.blit(txt_j, (rect_join_local.centerx - txt_j.get_width()//2, rect_join_local.centery - txt_j.get_height()//2))
            
            pygame.draw.rect(fenetre, coul_bouton_rouge, rect_stop_server)
            txt_s = police_corbel.render("Arrêter Serveur", True, (0,0,0))
            fenetre.blit(txt_s, (rect_stop_server.centerx - txt_s.get_width()//2, rect_stop_server.centery - txt_s.get_height()//2))

        pygame.display.flip()
        Horloge.tick(60)