import socket
import pickle
import struct

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
            # On utilise la nouvelle méthode de réception sécurisée
            return self.recv_obj() 
        except socket.error as e:
            print("Erreur de connexion :", e)
            return None

    def send(self, data):
        """
        Envoie des données et attend la réponse
        """
        try:
            # 1. On envoie nos données
            self.send_obj(data)
            # 2. On reçoit la réponse du serveur
            return self.recv_obj()
        except socket.error as e:
            print(e)
            return None
    
    def send_obj(self, data):
        """Envoie un objet précédé de sa taille (4 octets)"""
        msg = pickle.dumps(data)
        # On pack la taille du message dans 4 octets (big endian)
        length = struct.pack('>I', len(msg))
        self.client.sendall(length + msg)

    def recv_obj(self):
        """Reçoit un objet en lisant d'abord sa taille"""
        # 1. Lire les 4 premiers octets pour connaitre la taille
        raw_msglen = self.recvall(4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        
        # 2. Lire le reste des données exactement selon la taille
        data = self.recvall(msglen)
        return pickle.loads(data)

    def recvall(self, n):
        """Fonction utilitaire pour recevoir exactement n octets"""
        data = bytearray()
        while len(data) < n:
            packet = self.client.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data

    def close(self):
        self.client.close()