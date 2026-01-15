import socket
import json
import sys
import time

# Map Lane IDs to their Ports
LANE_PORTS = {'1': 5001, '2': 5002, '3': 5003, '4': 5004}

def send_emergency_signal(lane_id, vehicle_type="AMBULANCE"):
    target_port = LANE_PORTS.get(lane_id)
    if not target_port:
        print(f"Invalid Lane ID: {lane_id}")
        return

    print(f"🚑 [V2I] {vehicle_type} approaching Lane {lane_id}...")
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)
        s.connect(('localhost', target_port))
        
        # V2I Packet with High Priority
        packet = {
            "type": "V2I",
            "vehicle_type": vehicle_type,
            "priority": "HIGH",
            "action": "REQUEST_PREEMPTION"
        }
        
        s.sendall(json.dumps(packet).encode())
        s.close()
        print(f"✅ [V2I] Signal sent to Lane {lane_id} (Port {target_port})")
        
    except ConnectionRefusedError:
        print(f"❌ [ERROR] Lane {lane_id} is not running.")
    except Exception as e:
        print(f"❌ [ERROR] {e}")

if __name__ == "__main__":
    # Usage: python mock_vehicle.py <LANE_ID>
    lane = sys.argv[1] if len(sys.argv) > 1 else "1"
    send_emergency_signal(lane)