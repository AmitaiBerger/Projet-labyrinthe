import socket
from _thread import *
import pickle
import struct
import random
from Laby import Labyrinthe

# --- CONFIGURATION ---
MAX_PLAYERS = 2 # Sera modifié par run_server
current_players = 0
game_active = False
winner_id = -1
Labyr_commun = None
positions_joueurs = [] # Liste dynamique
server_socket = None
server_running = False

# --- FONCTIONS RESEAU (Inchangées, garde send_obj/recv_obj/recvall d'avant) ---
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
# ------------------------------------------------------------------

def reset_game():
    global Labyr_commun, positions_joueurs, winner_id, game_active
    print(f">>> NOUVELLE PARTIE ({MAX_PLAYERS} joueurs) <<<")
    Labyr_commun = Labyrinthe(15, 15)
    Labyr_commun.generer_par_Wilson()
    Labyr_commun.creuser_trous_intelligents()
    Labyr_commun.sortie = random.randint(0, len(Labyr_commun.cases) - 1)
    Labyr_commun.cases[Labyr_commun.sortie].est_sortie = True 
    
    # Appel de la nouvelle fonction N joueurs
    Labyr_commun.placer_n_joueurs(MAX_PLAYERS, ratio_eloignement=0.7)
    
    # On initialise les positions actuelles avec les positions de départ
    positions_joueurs = list(Labyr_commun.joueurs_indices)
    winner_id = -1
    game_active = False

def threaded_client(conn, player_id):
    global current_players, game_active, winner_id
    try:
        # On envoie: (Labyrinthe, mon_id, Nombre_Total_Joueurs)
        send_obj(conn, (Labyr_commun, player_id, MAX_PLAYERS))
    except:
        conn.close(); return

    while True:
        try:
            data = recv_obj(conn)
            if data is None: break
            
            # Mise à jour de la position de CE joueur
            positions_joueurs[player_id] = data
            
            # Démarrage quand la salle est pleine
            if current_players == MAX_PLAYERS and not game_active and winner_id == -1:
                game_active = True
                
            # Victoire
            if game_active and data == Labyr_commun.sortie and winner_id == -1:
                winner_id = player_id
                game_active = False # On arrête tout

            status = "PLAY"
            if winner_id != -1:
                status = "WIN" if winner_id == player_id else "LOSE"
            elif current_players < MAX_PLAYERS:
                status = "WAIT"
            
            # On renvoie TOUTES les positions + le status
            reply = (positions_joueurs, status)
            send_obj(conn, reply)
            
        except: break

    print(f"Joueur {player_id} parti.")
    current_players -= 1
    conn.close()
    if server_running and current_players <= 0:
        current_players = 0
        reset_game()

def run_server(nb_joueurs_choisis=2):
    global server_socket, current_players, server_running, MAX_PLAYERS
    MAX_PLAYERS = nb_joueurs_choisis # On met à jour le nombre attendu
    
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
            if not server_running: 
                conn.close(); break
            
            if current_players >= MAX_PLAYERS:
                conn.close(); continue
                
            current_players += 1
            start_new_thread(threaded_client, (conn, current_players - 1))
        except OSError: break
    print("Serveur Off")

def stop_server():
    global server_running, server_socket
    server_running = False
    if server_socket: server_socket.close()