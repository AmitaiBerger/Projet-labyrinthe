import socket
from _thread import *
import random
import time
from config import *
import random
import time
from Laby import Labyrinthe
from config import *
import pickle
import struct

# --- RÉSEAU ---
def envoyer_obj(sock, donnees):
    try:
        msg = pickle.dumps(donnees)
        longueur = struct.pack('>I', len(msg))
        sock.sendall(longueur + msg)
    except: pass

def recevoir_obj(sock):
    try:
        donnees = bytearray()
        while len(donnees) < 4:
            paquet = sock.recv(4 - len(donnees))
            if not paquet: return None
            donnees.extend(paquet)
        longueur_msg = struct.unpack('>I', donnees)[0]
        
        donnees = bytearray()
        while len(donnees) < longueur_msg:
            paquet = sock.recv(longueur_msg - len(donnees))
            if not paquet: return None
            donnees.extend(paquet)
        return pickle.loads(donnees)
    except: return None

# --- VARIABLES GLOBALES ---
NB_JOUEURS_MAX = 2
joueurs_actuels = 0
ids_connectes = []
partie_active = False
id_gagnant = -1
Labyr_commun = None
positions_joueurs = [] 
serveur_actif = True
socket_serveur = None

# Liste des événements récents à diffuser: [("ITEM_GONE", idx), ("WALL_BROKEN", idx, dir), ...]
evenements_jeu = [] 

def reinitialiser_jeu():
    global Labyr_commun, positions_joueurs, id_gagnant, partie_active, evenements_jeu
    print(f">>> GÉNÉRATION LABYRINTHE ({NB_JOUEURS_MAX} joueurs) <<<")
    Labyr_commun = Labyrinthe(15, 15)
    Labyr_commun.generer_par_Wilson()
    Labyr_commun.creuser_trous_intelligents()
    
    Labyr_commun.sortie = random.randint(0, len(Labyr_commun.cases)-1)
    Labyr_commun.cases[Labyr_commun.sortie].est_sortie = True
    Labyr_commun.cases[Labyr_commun.sortie].contenu = "Sortie"

    Labyr_commun.visibles()
    
    #Labyr_commun.placer_items() # Ajout Phase 2
    
    Labyr_commun.placer_n_joueurs(NB_JOUEURS_MAX)
    positions_joueurs = list(Labyr_commun.joueurs_indices_depart)
    id_gagnant = -1
    partie_active = False
    evenements_jeu = []

def client_thread(conn, id_joueur):
    global joueurs_actuels, partie_active, id_gagnant, ids_connectes, evenements_jeu, Labyr_commun
    
    if Labyr_commun:
        positions_joueurs[id_joueur] = Labyr_commun.joueurs_indices_depart[id_joueur]

    try:
        envoyer_obj(conn, (Labyr_commun, id_joueur, NB_JOUEURS_MAX))
    except:
        conn.close(); return

    while True:
        try:
            # Réception: Soit int (mouvement), soit tuple (Action)
            donnees = recevoir_obj(conn)
            if donnees is None: break
            
            # --- LOGIQUE DE JEU SERVEUR ---
            
            # 1. Cas Action Spéciale (Marteau, Item pris...)
            if isinstance(donnees, tuple):
                action = donnees[0]
                
                if action == "MOVE": # ("MOVE", new_idx, item_taken_id_opt)
                    nouvelle_pos = donnees[1]
                    positions_joueurs[id_joueur] = nouvelle_pos
                    
                    # Gestion Items qui disparaissent (CORRIGÉ)
                    if len(donnees) > 2 and donnees[2] is not None:
                        idx_item_supprime = donnees[2]
                        
                        # On utilise .pop(key, None) pour éviter le crash si l'item a déjà été supprimé
                        # par un autre thread ou une double requête.
                        type_item = Labyr_commun.items.pop(idx_item_supprime, None)
                        
                        if type_item: # Si on a bien supprimé quelque chose
                            evenements_jeu.append(("ITEM_GONE", idx_item_supprime))
                            
                            # Si TP, supprimer le jumeau de manière sécurisée
                            if type_item == ITEM_TELEPORT and idx_item_supprime in Labyr_commun.teleporters_links:
                                lien = Labyr_commun.teleporters_links[idx_item_supprime]
                                # Pareil, on pop en sécurité
                                if Labyr_commun.items.pop(lien, None):
                                    evenements_jeu.append(("ITEM_GONE", lien))

                elif action == "BREAK": # ("BREAK", idx_case, direction)
                    idx, direction = donnees[1], donnees[2]
                    # Appliquer au modèle serveur
                    c = Labyr_commun.cases[idx]
                    c.voisins[direction] = True
                    # Ouvrir le mur opposé
                    idx_oppose = -1
                    if direction == 0: idx_oppose = idx + 1
                    elif direction == 1: idx_oppose = idx - Labyr_commun.largeur
                    elif direction == 2: idx_oppose = idx - 1
                    elif direction == 3: idx_oppose = idx + Labyr_commun.largeur
                    
                    if 0 <= idx_oppose < len(Labyr_commun.cases):
                        Labyr_commun.cases[idx_oppose].voisins[(direction+2)%4] = True
                        
                    evenements_jeu.append(("WALL_BROKEN", idx, direction))

            # 2. Cas Mouvement Simple (Legacy support)
            elif isinstance(donnees, int):
                positions_joueurs[id_joueur] = donnees

            # --- VÉRIFICATION VICTOIRE ---
            if joueurs_actuels == NB_JOUEURS_MAX and not partie_active and id_gagnant == -1:
                partie_active = True
            
            pos_actuelle = positions_joueurs[id_joueur]
            if partie_active and pos_actuelle == Labyr_commun.sortie and id_gagnant == -1:
                id_gagnant = id_joueur
                partie_active = False
            
            statut = "PLAY"
            if id_gagnant != -1:
                statut = "WIN" if id_gagnant == id_joueur else "LOSE"
            elif joueurs_actuels < NB_JOUEURS_MAX:
                statut = "WAIT"
            
            # 3. ENVOI RÉPONSE (Positions + Status + Events)
            # On envoie les 10 derniers événements pour être sûr (simplification UDP-like sur TCP)
            evenements_a_envoyer = evenements_jeu[-20:] 
            reponse = (positions_joueurs, statut, joueurs_actuels, evenements_a_envoyer)
            envoyer_obj(conn, reponse)
            
        except Exception as e: 
            print(f"Erreur Client {id_joueur}: {e}")
            break
    
    print(f"Joueur {id_joueur} déconnecté.")
    ids_connectes[id_joueur] = False
    joueurs_actuels -= 1
    conn.close()
    
    if serveur_actif and joueurs_actuels <= 0:
        reinitialiser_jeu()

def lancer_serveur(nb):
    global socket_serveur, serveur_actif, NB_JOUEURS_MAX, ids_connectes, joueurs_actuels
    NB_JOUEURS_MAX = nb
    ids_connectes = [False] * NB_JOUEURS_MAX
    
    socket_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        socket_serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_serveur.bind(("0.0.0.0", 5555))
        socket_serveur.listen(NB_JOUEURS_MAX)
        print("Serveur ON")
    except Exception as e:
        print("Erreur Serveur:", e)
        return

    reinitialiser_jeu()
    joueurs_actuels = 0
    serveur_actif = True
    
    while serveur_actif:
        try:
            conn, addr = socket_serveur.accept()
            if not serveur_actif: break
            
            id_libre = -1
            for i in range(NB_JOUEURS_MAX):
                if not ids_connectes[i]:
                    id_libre = i
                    break
            
            if id_libre == -1:
                conn.close()
                continue
                
            ids_connectes[id_libre] = True
            joueurs_actuels += 1
            start_new_thread(client_thread, (conn, id_libre))
            
        except: break
    print("Serveur OFF")

def arreter_serveur():
    global serveur_actif, socket_serveur
    serveur_actif = False
    if socket_serveur: socket_serveur.close()