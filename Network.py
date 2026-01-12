import socket
import pickle

class Network:
    def __init__(self, ip="localhost"):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = ip
        self.port = 5555
        self.addr = (self.server, self.port)
        self.p = self.connect()

    def connect(self):
        try:
            self.client.connect(self.addr)
            return pickle.loads(self.client.recv(4096*16))
        except socket.error as e:
            print("Erreur de connexion :", e)
            return None

    def send(self, data):
        """
        Envoie sa position (int) 
        Reçoit (pos_adversaire, status)
        """
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(2048))
        except socket.error as e:
            print(e)
            return None
    
    def close(self):
        self.client.close()