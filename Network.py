import socket
import pickle

class Network:
    def __init__(self, ip="localhost"):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = ip
        self.port = 5555
        self.addr = (self.server, self.port)
        # Lors de la connexion, on récupère un tuple : (Labyrinthe, id_joueur)
        self.p = self.connect()

    def connect(self):
        try:
            self.client.connect(self.addr)
            # On augmente la taille du buffer car le Labyrinthe est un gros objet
            return pickle.loads(self.client.recv(4096*16))
        except socket.error as e:
            print("Erreur de connexion :", e)
            return None

    def send(self, data):
        """
        Envoie sa position (int) et reçoit celle de l'adversaire (int)
        """
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(2048))
        except socket.error as e:
            print(e)
            return None