import socket
import pickle

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "localhost" # "localhost" pour tester sur le même PC, ou l'IP du serveur
        self.port = 5555
        self.addr = (self.server, self.port)
        self.p = self.connect()

    def connect(self):
        try:
            self.client.connect(self.addr)
            # Au moment de la connexion, on reçoit le labyrinthe initial
            return pickle.loads(self.client.recv(4096*8)) 
        except:
            pass

    def send(self, data):
        """Envoyer sa position et recevoir celle de l'adversaire"""
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(2048*2))
        except socket.error as e:
            print(e)