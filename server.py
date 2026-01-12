import socket
from _thread import *
import pickle
from Laby import Labyrinthe # Le serveur doit connaitre la classe

# Configuration
#server = "localhost"
server = "0.0.0.0" # Ou "0.0.0.0" pour écouter sur tout le réseau local
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))

s.listen(2)
print("Serveur démarré, en attente de joueurs...")

# --- Génération du Labyrinthe COMMUN ---
# On fixe une taille pour le mode réseau (ex: 15x15)
Labyr_commun = Labyrinthe(15, 15)
Labyr_commun.generer_par_Wilson()
Labyr_commun.creuser_trous_intelligents()
Labyr_commun.sortie = Labyr_commun.cases[-1].i # Force une sortie si besoin
Labyr_commun.placer_deux_joueurs(ratio_eloignement=0.7)
print("Labyrinthe généré et prêt à être envoyé.")

# Stockage des positions [J1, J2]
positions_joueurs = [Labyr_commun.joueur1, Labyr_commun.joueur2]

def threaded_client(conn, player_id):
    # 1. Envoi initial : Le Labyrinthe complet + L'ID du joueur (0 ou 1)
    conn.send(pickle.dumps((Labyr_commun, player_id)))
    
    while True:
        try:
            # Réception de la position du joueur actuel
            data = pickle.loads(conn.recv(2048))
            
            if data is None:
                break
            
            # Mise à jour de la position sur le serveur
            positions_joueurs[player_id] = data
            
            # Renvoi de la position de l'AUTRE joueur
            # Si je suis 0, je veux voir 1. Si je suis 1, je veux voir 0.
            reply = positions_joueurs[1 - player_id]
            
            conn.sendall(pickle.dumps(reply))
        except:
            break

    print(f"Joueur {player_id} déconnecté")
    conn.close()

current_player = 0
while True:
    conn, addr = s.accept()
    print("Connecté à :", addr)

    start_new_thread(threaded_client, (conn, current_player))
    current_player += 1