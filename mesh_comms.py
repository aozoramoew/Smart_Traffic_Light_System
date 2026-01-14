import socket
import threading
import json

class MeshNode:
    def __init__(self, node_id, config):
        self.node_id = node_id
        self.port = config['port']
        # Map of neighbors to ports
        self.neighbors = config['neighbors'] 
        
        # New: Track if I have the token
        self.has_token = False
        
        t = threading.Thread(target=self.listen, daemon=True)
        t.start()

    def listen(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server.bind(('localhost', self.port))
            server.listen(10)
        except:
            print(f"[ERROR] Port {self.port} busy.")
            return

        while True:
            try:
                client, _ = server.accept()
                data = client.recv(1024).decode()
                if data:
                    msg = json.loads(data)
                    # Handle Token Handover
                    if msg.get("type") == "TOKEN":
                        print(f"[MESH] 🏁 Token Received from Node {msg['sender']}!")
                        self.has_token = True
                client.close()
            except:
                pass

    def pass_token(self, target_node_id):
        """Pass the turn to the next node"""
        target_port = self.neighbors.get(target_node_id)
        if not target_port: return

        packet = {"sender": self.node_id, "type": "TOKEN"}
        
        try:
            print(f"[MESH] ➡️ Passing Token to Node {target_node_id}...")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.1)
            s.connect(('localhost', target_port))
            s.sendall(json.dumps(packet).encode())
            s.close()
            self.has_token = False # I no longer have the turn
        except:
            print(f"[ERROR] Could not pass token to Node {target_node_id}")