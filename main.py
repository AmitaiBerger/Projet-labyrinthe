from Laby import *
import Affichage
from Affichage import Camera
import sys 
import pygame
import Joueur
from Network import Network
import socket
import threading
import server as server_module # On importe notre module serveur modifié

pygame.init()

# --- COULEURS ET STYLE ---
COULEUR_FOND = (240, 240, 245)
COULEUR_BOUTON = (52, 152, 219) # Bleu moderne
COULEUR_BOUTON_HOVER = (41, 128, 185)
COULEUR_TEXTE = (255, 255, 255)
COULEUR_TITRE = (44, 62, 80)
FONT_TITRE = pygame.font.SysFont('Arial', 60, bold=True)
FONT_BOUTON = pygame.font.SysFont('Arial', 30)
FONT_NORMAL = pygame.font.SysFont('Arial', 24)

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

class Button:
    def __init__(self, text, x, y, w, h, action_key=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action_key = action_key
        self.is_hovered = False

    def draw(self, surface):
        color = COULEUR_BOUTON_HOVER if self.is_hovered else COULEUR_BOUTON
        # Ombre légère
        pygame.draw.rect(surface, (200, 200, 200), (self.rect.x+3, self.rect.y+3, self.rect.width, self.rect.height), border_radius=12)
        # Bouton
        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        
        # Texte centré
        txt_surf = FONT_BOUTON.render(self.text, True, COULEUR_TEXTE)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

# --- FONCTION DU JEU (Légèrement nettoyée) ---
def partie(taille_laby=(10,10), mode_de_jeu="solo", ip_serveur="localhost", debug=False):
    # Initialisation fenêtre de jeu
    res = (720,720)
    fenetre = pygame.display.set_mode(res)
    pygame.display.set_caption("Jeu de Labyrinthe - En Partie")
    Horloge = pygame.time.Clock()
    
    # ... (Chargement réseau identique à avant) ...
    joueurs = []
    mon_id = 0
    reseau = None
    J_Moi = None
    J_Autre = None
    
    if mode_de_jeu == "reseau":
        # Petit écran chargement
        fenetre.fill(COULEUR_FOND)
        txt = FONT_NORMAL.render(f"Connexion à {ip_serveur}...", True, (0,0,0))
        fenetre.blit(txt, (res[0]//2 - txt.get_width()//2, res[1]//2))
        pygame.display.update()

        reseau = Network(ip_serveur)
        if reseau.p is None:
            return # Retour au menu si échec

        Labyr, mon_id = reseau.p
        Labyr.visibles()
        
        J1 = Joueur.Joueur(Labyr, Labyr.cases[Labyr.joueur1], (255,0,0), 4, 5)
        J2 = Joueur.Joueur(Labyr, Labyr.cases[Labyr.joueur2], (0,0,255), 4, 5)
        
        if mon_id == 0:
            J_Moi = J1
            J_Autre = J2
        else:
            J_Moi = J2
            J_Autre = J1
        joueurs = [J_Moi, J_Autre]
        J_Moi.voir()
        
    else:
        # Mode Solo/Robot
        Labyr = Labyrinthe(taille_laby[1], taille_laby[0])
        Labyr.generer_par_Wilson()
        Labyr.visibles()
        if mode_de_jeu == "solo":
            Labyr.placer_depart(ratio_distance_min=0.7)
            J_Moi = Joueur.Joueur(Labyr, Labyr.cases[Labyr.depart], (255,0,0), 4, 5)
            joueurs = [J_Moi]
        elif mode_de_jeu == "robot":
            Labyr.placer_deux_joueurs()
            J_Moi = Joueur.Joueur(Labyr, Labyr.cases[Labyr.joueur1], (255,0,0), 4, 5)
            BOT = Joueur.Joueur(Labyr, Labyr.cases[Labyr.joueur2], (0,0,255), 4, 5)
            joueurs = [J_Moi, BOT]
        J_Moi.voir()

    # Caméra
    cam = Camera()
    cam.centrage = J_Moi
    cam.hauteur_vision = 12 if mode_de_jeu == "reseau" else min(Labyr.hauteur, Labyr.largeur)
    cam.largeur_vision = cam.hauteur_vision

    Sortie = False
    Defaite = False
    GameStatus = "PLAY"
    duree_totale = 0
    touches = [pygame.K_z, pygame.K_q, pygame.K_s, pygame.K_d]

    while not Sortie:
        can_move = True
        
        if mode_de_jeu == "reseau":
            try:
                reponse = reseau.send(J_Moi.get_case_absolue())
                if reponse:
                    pos_autre, GameStatus = reponse
                    J_Autre.set_case_absolue(pos_autre)
                    if GameStatus == "WAIT": can_move = False
                    elif GameStatus == "WIN": Sortie = True; Defaite = False
                    elif GameStatus == "LOSE": Sortie = True; Defaite = True
                else:
                    Sortie = True # Déconnexion
            except: Sortie = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Sortie = True
                Defaite = True
            if event.type == pygame.KEYDOWN and can_move:
                Affichage.effacer_joueur(fenetre, J_Moi, 720, camera=cam)
                J_Moi.changement_direction(event.key, touches)
                J_Moi.deplacement()
                J_Moi.voir()
                if mode_de_jeu != "reseau" and J_Moi.get_case_absolue() == Labyr.sortie:
                    Sortie = True
                    Defaite = False

        Affichage.tout_effacer(fenetre, COULEUR_FOND)
        
        if mode_de_jeu == "reseau" and not can_move:
            txt = FONT_TITRE.render("En attente...", True, (0,0,0))
            fenetre.blit(txt, (360 - txt.get_width()//2, 360))
        else:
            Affichage.affiche_ensemble_de_cases(fenetre,Labyr,J_Moi.cases_vues,720,coul_mur=(150,150,150),camera=cam)
            Affichage.affiche_ensemble_de_cases(fenetre,Labyr,J_Moi.visu_actuel,720,coul_mur=(0,0,0),camera=cam)
            for j in joueurs: Affichage.afficher_joueur(fenetre,j,720,camera=cam)

        pygame.display.update()
        Horloge.tick(60)
        if can_move: duree_totale += Horloge.get_time()

    if mode_de_jeu == "reseau": reseau.close()
    
    if not Defaite:
        affiche_fenetre_victoire(duree_totale/1000)
    elif mode_de_jeu == "reseau":
        affiche_fenetre_defaite()

def affiche_fenetre_victoire(temps):
    fen = pygame.display.set_mode((500, 200))
    fen.fill(COULEUR_FOND)
    txt = FONT_NORMAL.render(f"Victoire en {round(temps, 2)} secondes !", True, (46, 204, 113))
    fen.blit(txt, (250 - txt.get_width()//2, 80))
    pygame.display.update()
    pygame.time.delay(3000)

def affiche_fenetre_defaite():
    fen = pygame.display.set_mode((500, 200))
    fen.fill(COULEUR_FOND)
    txt = FONT_NORMAL.render("L'adversaire a gagné !", True, (231, 76, 60))
    fen.blit(txt, (250 - txt.get_width()//2, 80))
    pygame.display.update()
    pygame.time.delay(3000)

# --- MENU PRINCIPAL (NOUVEAU) ---

def menu_principal():
    largeur_win = 800
    hauteur_win = 600
    fenetre = pygame.display.set_mode((largeur_win, hauteur_win))
    pygame.display.set_caption("Labyrinthe - Menu Principal")
    
    # Création des boutons
    btn_solo = Button("Mode Solo", 300, 200, 200, 50)
    btn_robot = Button("VS Robot", 300, 270, 200, 50)
    btn_host = Button("Héberger Serveur", 300, 340, 200, 50) # Nouveau
    btn_join = Button("Rejoindre une partie", 300, 410, 200, 50)
    btn_quit = Button("Quitter", 300, 500, 200, 50)
    
    buttons = [btn_solo, btn_robot, btn_host, btn_join, btn_quit]
    
    server_thread = None
    local_ip = get_local_ip()
    host_mode = False
    
    input_ip = "127.0.0.1"
    join_mode = False

    clock = pygame.time.Clock()

    while True:
        pos_souris = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Gestion Saisie IP (si mode rejoindre)
            if join_mode:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # Lancer la connexion
                        partie((10,10), mode_de_jeu="reseau", ip_serveur=input_ip)
                        fenetre = pygame.display.set_mode((largeur_win, hauteur_win)) # Reset fenetre menu
                        join_mode = False
                    elif event.key == pygame.K_BACKSPACE:
                        input_ip = input_ip[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        join_mode = False
                    else:
                        input_ip += event.unicode
            
            # Gestion Boutons Menu
            elif not host_mode:
                if btn_solo.is_clicked(event):
                    partie((15,15), "solo")
                    fenetre = pygame.display.set_mode((largeur_win, hauteur_win))
                
                elif btn_robot.is_clicked(event):
                    partie((15,15), "robot")
                    fenetre = pygame.display.set_mode((largeur_win, hauteur_win))
                
                elif btn_host.is_clicked(event):
                    # Démarrer le serveur dans un thread
                    if server_thread is None:
                        server_thread = threading.Thread(target=server_module.run_server)
                        server_thread.daemon = True # Le serveur se coupera si on ferme le jeu
                        server_thread.start()
                    host_mode = True
                
                elif btn_join.is_clicked(event):
                    join_mode = True
                    input_ip = "" # Reset pour écrire
                
                elif btn_quit.is_clicked(event):
                    pygame.quit()
                    sys.exit()

            # Gestion Clics en mode Host
            elif host_mode:
                # Un bouton pour lancer la partie locale (se connecter à soi-même)
                btn_start_host = Button("Lancer ma partie", 300, 450, 200, 50)
                if btn_start_host.is_clicked(event):
                    partie((10,10), mode_de_jeu="reseau", ip_serveur="localhost")
                    fenetre = pygame.display.set_mode((largeur_win, hauteur_win))
                    host_mode = False 
                    # Note : le serveur continue de tourner en arrière plan, c'est parfait pour enchainer

        # --- DESSIN ---
        fenetre.fill(COULEUR_FOND)
        
        # Titre
        titre = FONT_TITRE.render("LABYRINTHE", True, COULEUR_TITRE)
        fenetre.blit(titre, (largeur_win//2 - titre.get_width()//2, 80))

        if join_mode:
            # Affichage saisie IP
            txt_instruct = FONT_NORMAL.render("Entrez l'IP de l'hôte et appuyez sur Entrée :", True, (0,0,0))
            fenetre.blit(txt_instruct, (largeur_win//2 - txt_instruct.get_width()//2, 250))
            
            # Boite de texte
            pygame.draw.rect(fenetre, (255,255,255), (250, 300, 300, 50))
            pygame.draw.rect(fenetre, (0,0,0), (250, 300, 300, 50), 2)
            txt_ip = FONT_BOUTON.render(input_ip, True, (0,0,0))
            fenetre.blit(txt_ip, (260, 310))
            
            txt_esc = FONT_NORMAL.render("Échap pour annuler", True, (100,100,100))
            fenetre.blit(txt_esc, (largeur_win//2 - txt_esc.get_width()//2, 400))

        elif host_mode:
            # Affichage Lobby Host
            txt_status = FONT_NORMAL.render("Serveur démarré !", True, (39, 174, 96))
            fenetre.blit(txt_status, (largeur_win//2 - txt_status.get_width()//2, 200))
            
            # Affichage IP en GROS
            txt_ip_label = FONT_BOUTON.render(f"Votre IP LAN est : {local_ip}", True, (0,0,0))
            fenetre.blit(txt_ip_label, (largeur_win//2 - txt_ip_label.get_width()//2, 250))
            
            txt_info = FONT_NORMAL.render("Donnez cette IP au deuxième joueur.", True, (100,100,100))
            fenetre.blit(txt_info, (largeur_win//2 - txt_info.get_width()//2, 300))
            
            # Bouton pour rejoindre soi-même
            btn_start_host = Button("Rejoindre (Hôte)", 300, 450, 200, 50)
            btn_start_host.check_hover(pos_souris)
            btn_start_host.draw(fenetre)

        else:
            # Affichage Menu Normal
            for btn in buttons:
                btn.check_hover(pos_souris)
                btn.draw(fenetre)

        pygame.display.flip()
        clock.tick(60)

if __name__=="__main__":
    menu_principal()