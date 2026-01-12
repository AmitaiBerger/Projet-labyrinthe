import socket
from _thread import *
import pickle
import struct
import random
from Laby import Labyrinthe

# --- VARIABLES GLOBALES ---
current_players = 0
game_active = False
winner_id = -1
Labyr_commun = None
positions_joueurs = [0, 0]
server_socket = None # Pour pouvoir le fermer si besoin

# --- FONCTIONS RESEAU ---
def send_obj(sock, data):
    try:
        msg = pickle.dumps(data)
        length = struct.pack('>I', len(msg))
        sock.sendall(length + msg)
    except:
        pass

def recv_obj(sock):
    try:
        raw_msglen = recvall(sock, 4)
        if not raw_msglen: return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        data = recvall(sock, msglen)
        return pickle.loads(data)
    except:
        return None

def recvall(sock, n):
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet: return None
        data.extend(packet)
    return data

def reset_game():
    global Labyr_commun, positions_joueurs, winner_id, game_active
    print(">>> CRÉATION D'UNE NOUVELLE PARTIE <<<")
    Labyr_commun = Labyrinthe(15, 15)
    Labyr_commun.generer_par_Wilson()
    Labyr_commun.creuser_trous_intelligents()
    Labyr_commun.sortie = random.randint(0, len(Labyr_commun.cases) - 1)
    Labyr_commun.cases[Labyr_commun.sortie].est_sortie = True 
    Labyr_commun.placer_deux_joueurs(ratio_eloignement=0.7)
    positions_joueurs = [Labyr_commun.joueur1, Labyr_commun.joueur2]
    winner_id = -1
    game_active = False

def threaded_client(conn, player_id):
    global current_players, game_active, winner_id
    try:
        send_obj(conn, (Labyr_commun, player_id))
    except:
        conn.close()
        return

    while True:
        try:
            data = recv_obj(conn)
            if data is None: break
            
            positions_joueurs[player_id] = data
            
            if current_players == 2 and not game_active and winner_id == -1:
                game_active = True
                
            if game_active and data == Labyr_commun.sortie and winner_id == -1:
                winner_id = player_id
                game_active = False

            status = "PLAY"
            if winner_id != -1:
                status = "WIN" if winner_id == player_id else "LOSE"
            elif current_players < 2:
                status = "WAIT"
            else:
                status = "PLAY"
                
            reply = (positions_joueurs[1 - player_id], status)
            send_obj(conn, reply)
            
        except:
            break

    print(f"Joueur {player_id} déconnecté")
    current_players -= 1
    conn.close()
    if current_players <= 0:
        current_players = 0
        reset_game()

# --- FONCTION PRINCIPALE (appelée par le menu) ---
def run_server():
    global server_socket, current_players
    server = "0.0.0.0"
    port = 5555

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((server, port))
    except socket.error as e:
        print(str(e))
        return

    server_socket.listen(2)
    print("Serveur démarré en arrière-plan...")
    
    reset_game()
    current_players = 0

    while True:
        try:
            conn, addr = server_socket.accept()
            if current_players >= 2:
                conn.close()
                continue
            current_players += 1
            start_new_thread(threaded_client, (conn, current_players - 1))
        except OSError:
            # Arrive quand on coupe le socket manuellement
            break