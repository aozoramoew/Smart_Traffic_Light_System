import cv2
import sys
import logging
import time
import socket
import json
from ultralytics import YOLO
from mesh_comms import MeshNode

logging.getLogger("ultralytics").setLevel(logging.WARNING)

# ==========================================
# 1. ROUND ROBIN CONFIGURATION
# ==========================================
ALL_PORTS = {'1': 5001, '2': 5002, '3': 5003, '4': 5004}
node_id = "1" 
if len(sys.argv) > 1: node_id = sys.argv[1]

my_port = ALL_PORTS.get(node_id, 5001)
my_neighbors = {nid: port for nid, port in ALL_PORTS.items() if nid != node_id}
config = {"port": my_port, "neighbors": my_neighbors}

# DEFINE THE CYCLE: Who is next?
# 1(N) -> 2(E) -> 3(S) -> 4(W) -> 1(N)
NEXT_NODE_MAP = {"1": "2", "2": "3", "3": "4", "4": "1"}
next_node = NEXT_NODE_MAP[node_id]

print(f"--- STARTING LANE {node_id} ---")
print(f"--- I will pass token to Lane {next_node} ---")

mesh = MeshNode(node_id, config)

# INITIAL STARTUP:
# Node 1 starts with the Token (Green)
if node_id == "1":
    mesh.has_token = True
    print("[STARTUP] Node 1 taking initial control.")

# ==========================================
# 2. VISUALIZER SENDER
# ==========================================
def send_data_to_viz(lane_id, car_count, request_green):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.02) 
        s.connect(('localhost', 9999))
        packet = {"lane_id": int(lane_id), "car_count": int(car_count), "request_green": bool(request_green)}
        s.sendall(json.dumps(packet).encode())
        s.close()
    except: pass 

# ==========================================
# 3. VIDEO SETUP
# ==========================================
VIDEO_FILES = {"1": "node1.mp4", "2": "node2.mp4", "3": "node3.mp4", "4": "node4.mp4"}
video_source = VIDEO_FILES.get(node_id, "traffic.mp4")
cap = cv2.VideoCapture(video_source)
if not cap.isOpened(): cap = cv2.VideoCapture(0)

ret, first_frame = cap.read()
if not ret: sys.exit()
last_frame = cv2.resize(first_frame, (640, 360))

model = YOLO('yolov8n.pt') 
VEHICLE_CLASSES = [2, 3, 5, 7] 

# ==========================================
# 4. TRAFFIC STATE MACHINE
# ==========================================
state = "RED"       # Start RED (unless has_token set above)
timer = 0           
vehicle_count = 0
last_time_check = time.time()

# If I start with token (Node 1), jump straight to Green logic
if mesh.has_token:
    state = "CALC_TIME" # Special state to trigger calculation immediately

while True:
    current_time = time.time()
    dt = current_time - last_time_check
    last_time_check = current_time

    # --- A. VIDEO CONTROL ---
    if state == "GREEN":
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = cap.read()
        frame = cv2.resize(frame, (640, 360))
        last_frame = frame.copy()
    else:
        # Yellow or Red = Freeze
        frame = last_frame.copy()

    # --- B. AI DETECTION ---
    results = model.predict(frame, classes=VEHICLE_CLASSES, verbose=False, conf=0.4)
    vehicle_count = len(results[0].boxes)
    annotated_frame = results[0].plot()

    # --- C. ROUND ROBIN LOGIC ---

    # STATE 1: RED (Waiting for Token)
    if state == "RED":
        if mesh.has_token:
            # I just got the token from neighbor!
            print(f"[LOGIC] Token Received! Analyzing traffic...")
            state = "CALC_TIME"

    # STATE 2: CALCULATE TIME (Instant transition)
    elif state == "CALC_TIME":
        # Check if I actually have cars
        if vehicle_count > 0:
            # Standard AI Formula: 2s per car
            calculated = vehicle_count * 2.0
            timer = max(5.0, min(calculated, 40.0)) # Min 5s, Max 40s
            state = "GREEN"
            print(f"[DECISION] Going GREEN for {timer:.1f}s")
        else:
            # I am empty! Don't waste time.
            # Go Green very briefly just to show I'm alive, then pass.
            timer = 2.0 
            state = "GREEN" 
            print("[DECISION] Lane Empty. Skipping turn (2s Green).")

    # STATE 3: GREEN (Active)
    elif state == "GREEN":
        timer -= dt
        if timer <= 0:
            state = "YELLOW"
            timer = 3.0 # Fixed 3s Yellow
            print("[TIMER] Green ended. Switching Yellow.")

    # STATE 4: YELLOW (Transition)
    elif state == "YELLOW":
        timer -= dt
        if timer <= 0:
            # Handover Time!
            print(f"[HANDOVER] Cycle Complete. Passing to Node {next_node}")
            mesh.pass_token(next_node) # Send network message
            mesh.has_token = False     # Reset my flag
            state = "RED"

    # --- D. SYNC WITH SIMULATOR ---
    # Only request Green on the simulator if I am GREEN
    send_data_to_viz(node_id, vehicle_count, (state == "GREEN"))

    # --- E. VISUALS ---
    if state == "GREEN":
        color = (0, 255, 0) # Green
        text = f"GREEN: {int(timer)}s"
    elif state == "YELLOW":
        color = (0, 255, 255) # Yellow
        text = f"YELLOW: {int(timer)}s"
    else:
        color = (0, 0, 255) # Red
        text = "RED (Waiting)"

    cv2.circle(annotated_frame, (580, 50), 30, color, -1)
    cv2.putText(annotated_frame, text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)
    cv2.putText(annotated_frame, f"Cars: {vehicle_count}", (10, 340), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    cv2.imshow(f"Lane {node_id} Camera", annotated_frame)
    if cv2.waitKey(30) & 0xFF == 27: break

cap.release()
cv2.destroyAllWindows()