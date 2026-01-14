import socket
from _thread import *
import pickle
import struct
import random
from Laby import Labyrinthe

# --- CONFIGURATION ---
MAX_PLAYERS = 2
current_players = 0
game_active = False
winner_id = -1
Labyr_commun = None
positions_joueurs = []
server_socket = None
server_running = False
connected_ids = []

# --- FONCTIONS RESEAU (Inchangées) ---
def send_obj(sock, data):
    try:
        msg = pickle.dumps(data)
        length = struct.pack('>I', len(msg))
        sock.sendall(length + msg)
    except: pass

def recv_obj(sock):
    try:
        raw_msglen = recvall(sock, 4)
        if not raw_msglen: return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        data = recvall(sock, msglen)
        return pickle.loads(data)
    except: return None

def recvall(sock, n):
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet: return None
        data.extend(packet)
    return data

def reset_game():
    global Labyr_commun, positions_joueurs, winner_id, game_active
    print(f">>> NOUVELLE PARTIE ({MAX_PLAYERS} joueurs) <<<")
    Labyr_commun = Labyrinthe(15, 15)
    Labyr_commun.generer_par_Wilson()
    Labyr_commun.creuser_trous_intelligents()
    Labyr_commun.sortie = random.randint(0, len(Labyr_commun.cases) - 1)
    Labyr_commun.cases[Labyr_commun.sortie].est_sortie = True 
    Labyr_commun.cases[Labyr_commun.sortie].contenu = "Sortie"
    Labyr_commun.placer_n_joueurs(MAX_PLAYERS, ratio_eloignement=0.7)
    positions_joueurs = list(Labyr_commun.joueurs_indices)
    winner_id = -1
    game_active = False

def threaded_client(conn, player_id):
    global current_players, game_active, winner_id, connected_ids # <-- AJOUTE connected_ids
    
    # AJOUT ICI : On réinitialise la position de ce slot au point de départ
    # (Pour éviter de reprendre la partie là où le précédent joueur s'est déconnecté)
    if Labyr_commun and positions_joueurs:
        positions_joueurs[player_id] = Labyr_commun.joueurs_indices[player_id]

    try:
        send_obj(conn, (Labyr_commun, player_id, MAX_PLAYERS))
    except:
        conn.close(); return

    while True:
        try:
            data = recv_obj(conn)
            if data is None: break
            
            positions_joueurs[player_id] = data
            
            if current_players == MAX_PLAYERS and not game_active and winner_id == -1:
                game_active = True
                
            if game_active and data == Labyr_commun.sortie and winner_id == -1:
                winner_id = player_id
                game_active = False

            status = "PLAY"
            if winner_id != -1:
                status = "WIN" if winner_id == player_id else "LOSE"
            elif current_players < MAX_PLAYERS:
                status = "WAIT"
            
            reply = (positions_joueurs, status)
            send_obj(conn, reply)
            
        except: break

    print(f"Joueur {player_id} parti.")
    
    # --- MODIFICATION IMPORTANTE ICI (FIN DE FONCTION) ---
    connected_ids[player_id] = False # On libère ce slot spécifique (ex: le slot 0 se libère)
    current_players -= 1
    
    if not game_active and winner_id == -1:
        print(f"Une place se libère. En attente : {current_players}/{MAX_PLAYERS}")
    
    conn.close()
    if server_running and current_players <= 0:
        current_players = 0
        reset_game()

def run_server(nb_joueurs_choisis=2):
    global server_socket, current_players, server_running, MAX_PLAYERS, connected_ids
    MAX_PLAYERS = nb_joueurs_choisis
    
    # Initialisation de la liste des slots (Tous False au début)
    connected_ids = [False] * MAX_PLAYERS 
    
    server = "0.0.0.0"
    port = 5555
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((server, port))
    except socket.error as e: print(str(e)); return

    server_socket.listen(MAX_PLAYERS)
    print(f"Serveur démarré pour {MAX_PLAYERS} joueurs...")
    
    reset_game()
    current_players = 0
    server_running = True

    while server_running:
        try:
            conn, addr = server_socket.accept()
            if not server_running: conn.close(); break
            
            # --- NOUVELLE LOGIQUE D'ATTRIBUTION ---
            # On cherche le premier ID libre (False) dans la liste
            free_id = -1
            for i in range(MAX_PLAYERS):
                if not connected_ids[i]:
                    free_id = i
                    break
            
            # Si on n'a pas trouvé de place libre (Serveur plein)
            if free_id == -1:
                print("Tentative de connexion rejetée : Serveur plein.")
                conn.close()
                continue
                
            # On valide l'entrée
            connected_ids[free_id] = True # On marque le slot comme pris
            current_players += 1
            start_new_thread(threaded_client, (conn, free_id))
            # --------------------------------------

        except OSError: break
    print("Serveur Off")

def stop_server():
    global server_running, server_socket
    server_running = False
    if server_socket: server_socket.close()