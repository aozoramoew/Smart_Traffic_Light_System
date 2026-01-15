import socket
import threading
import json
import time

class MeshNode:
    def __init__(self, node_id, config):
        self.node_id = node_id
        self.port = config['port']
        self.neighbors = config['neighbors'] 
        
        # State Flags
        self.has_token = False
        self.emergency_mode = False       
        self.emergency_vehicle_type = ""  
        self.yield_request = None         
        self.return_addr = None           

        t = threading.Thread(target=self.listen, daemon=True)
        t.start()

    def listen(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server.bind(('localhost', self.port))
            server.listen(10)
        except Exception as e:
            print(f"[ERROR] Port {self.port} failed to bind: {e}")
            return

        while True:
            try:
                client, _ = server.accept()
                data = client.recv(1024).decode()
                if data:
                    msg = json.loads(data)
                    
                    if msg.get("type") == "TOKEN":
                        print(f"[MESH] 🏁 Token Received from {msg.get('sender', 'Unknown')}")
                        self.has_token = True
                        self.return_addr = msg.get("return_to") 
                        if self.return_addr:
                            print(f"[MESH] 📝 Note: Must return token to Node {self.return_addr}")

                    elif msg.get("type") == "V2I" and msg.get("priority") == "HIGH":
                        print(f"[V2I] 🚨 {msg['vehicle_type']} DETECTED! Requesting Green...")
                        self.emergency_mode = True
                        self.emergency_vehicle_type = msg['vehicle_type']
                        self.broadcast_preemption() 

                    elif msg.get("type") == "PREEMPT_REQUEST":
                        sender = msg['sender']
                        # Only accept preempt if it's NOT from myself
                        if sender != self.node_id:
                            print(f"[MESH] ⚠️  Node {sender} requesting Emergency Yield!")
                            self.yield_request = sender

                    # --- NEW: CLEAR STALE REQUESTS ---
                    elif msg.get("type") == "EMERGENCY_END":
                        print("[MESH] ✅ Emergency Ended. Clearing yield requests.")
                        self.yield_request = None

                client.close()
            except: pass

    def broadcast_preemption(self):
        packet = {"type": "PREEMPT_REQUEST", "sender": self.node_id}
        for n_id, n_port in self.neighbors.items():
            self._send_packet(n_port, packet)

    # --- NEW FUNCTION ---
    def broadcast_emergency_end(self):
        """Tell everyone the emergency is over"""
        packet = {"type": "EMERGENCY_END", "sender": self.node_id}
        for n_id, n_port in self.neighbors.items():
            self._send_packet(n_port, packet)

    def pass_token(self, target_node_id, return_to_me=False):
        target_port = self.neighbors.get(target_node_id)
        if not target_port: 
            print(f"[ERROR] Target Node {target_node_id} unknown.")
            return

        packet = {
            "type": "TOKEN", 
            "sender": self.node_id,
            "return_to": self.node_id if return_to_me else None
        }
        
        print(f"[MESH] ➡️  Passing Token to Node {target_node_id}...")
        if self._send_packet(target_port, packet):
            self.has_token = False 
            self.yield_request = None 
            if not return_to_me: 
                self.return_addr = None
        else:
            print(f"[ERROR] Failed to send token to Node {target_node_id}")

    def _send_packet(self, port, packet):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.2)
            s.connect(('localhost', port))
            s.sendall(json.dumps(packet).encode())
            s.close()
            return True
        except:
            return False