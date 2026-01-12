import socket
from _thread import *
import pickle
import time
from Laby import Labyrinthe

server = "0.0.0.0"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))

s.listen(2)
print("Serveur démarré, en attente de connexions...")

# --- VARIABLES GLOBALES DU JEU ---
current_players = 0
game_active = False
winner_id = -1
Labyr_commun = None
positions_joueurs = [0, 0]

def reset_game():
    """Génère un nouveau labyrinthe pour une nouvelle session"""
    global Labyr_commun, positions_joueurs, winner_id, game_active
    print(">>> GÉNÉRATION D'UN NOUVEAU LABYRINTHE <<<")
    Labyr_commun = Labyrinthe(15, 15)
    Labyr_commun.generer_par_Wilson()
    Labyr_commun.creuser_trous_intelligents()
    # On force la sortie sur la dernière case
    Labyr_commun.sortie = Labyr_commun.cases[-1].i 
    Labyr_commun.placer_deux_joueurs(ratio_eloignement=0.7)
    
    positions_joueurs = [Labyr_commun.joueur1, Labyr_commun.joueur2]
    winner_id = -1
    game_active = False # On attendra 2 joueurs pour passer à True

# On génère le premier labyrinthe au lancement
reset_game()

def threaded_client(conn, player_id):
    global current_players, game_active, winner_id
    
    # 1. Envoi initial (Labyrinthe + ID)
    conn.send(pickle.dumps((Labyr_commun, player_id)))
    
    while True:
        try:
            # Réception de la position
            # On attend maintenant une simple position (int)
            data = pickle.loads(conn.recv(2048))
            
            if data is None:
                break
            
            # Mise à jour position
            positions_joueurs[player_id] = data
            
            # --- LOGIQUE DE JEU CÔTÉ SERVEUR ---
            
            # 1. Vérifier si on lance la partie (2 joueurs présents)
            if current_players == 2 and not game_active and winner_id == -1:
                game_active = True
                
            # 2. Vérifier la victoire
            if game_active and data == Labyr_commun.sortie and winner_id == -1:
                winner_id = player_id
                game_active = False # On arrête le jeu
                print(f"Le joueur {player_id} a gagné !")

            # 3. Préparer la réponse
            # Format: (Position_Adversaire, Statut_Jeu)
            # Statuts possibles : "WAIT", "PLAY", "WIN", "LOSE"
            
            status = "WAIT"
            if current_players < 2:
                status = "WAIT"
            elif winner_id != -1:
                if winner_id == player_id:
                    status = "WIN"
                else:
                    status = "LOSE"
            else:
                status = "PLAY"
                
            reply = (positions_joueurs[1 - player_id], status)
            
            conn.sendall(pickle.dumps(reply))
        except Exception as e:
            print(f"Erreur joueur {player_id}: {e}")
            break

    print(f"Joueur {player_id} déconnecté")
    current_players -= 1
    conn.close()
    
    # Si plus personne n'est là, on reset pour la prochaine équipe
    if current_players <= 0:
        current_players = 0 # Sécurité
        reset_game()

# Boucle principale d'acceptation
while True:
    conn, addr = s.accept()
    print("Connecté à :", addr)
    
    # Si on essaie de se connecter alors qu'il y a déjà 2 joueurs
    if current_players >= 2:
        print("Serveur plein, connexion refusée")
        conn.close()
        continue

    current_players += 1
    # Le premier arrivé est 0, le deuxième est 1
    p_id = current_players - 1 
    start_new_thread(threaded_client, (conn, p_id))