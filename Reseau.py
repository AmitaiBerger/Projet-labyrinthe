import socket
import pickle
import struct

# contient juste la classe Reseau
# qui définit une connexion client-serveur

class Reseau:
    def __init__(self, ip="localhost", port=5555):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = (ip, port)
        self.data_initiale = self.connect()

    def connect(self):
        try:
            self.client.connect(self.addr)
            return self.recv_obj()
        except Exception as e:
            print(f"Erreur Reseau: {e}")
            return None

    def send(self, data):
        try:
            self.send_obj(data)
            return self.recv_obj()
        except socket.error as e:
            print(e)
            return None
    
    def env_obj(self, data):
        msg = pickle.dumps(data)
        # Préfixe avec la taille (4 bytes big-endian)
        length = struct.pack('>I', len(msg))
        self.client.sendall(length + msg)

    def recv_obj(self):
        raw_msglen = self.recvall(4)
        if not raw_msglen: return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        return pickle.loads(self.recvall(msglen))

    def recvtout(self, n):
        data = bytearray()
        while len(data) < n:
            packet = self.client.recv(n - len(data))
            if not packet: return None
            data.extend(packet)
        return data

    def fermer(self):
        self.client.fermer()