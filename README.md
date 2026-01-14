# Smart Distributed Traffic Management System

![Smart Traffic Intersection Isometric View](https://img.freepik.com/free-vector/city-intersection-traffic-navigation-isometric-view_1284-17737.jpg?w=2000)

**User Guide & Running Instructions**

This project implements a distributed AI traffic system where 4 separate camera nodes monitor a single intersection. They use a **Token Ring (Round Robin)** protocol to pass the "Green Light" authority efficiently from North → East → South → West.

---

## 1. System Topology
Each Python instance represents one "Smart Camera" looking at one lane.

| Node ID | Direction | Video Source | Role |
| :--- | :--- | :--- | :--- |
| **Node 1** | **NORTH** | `node1.mp4` | **Leader** (Starts with Green Token) |
| **Node 2** | **EAST** | `node2.mp4` | Follows Node 1 |
| **Node 3** | **SOUTH** | `node3.mp4` | Follows Node 2 |
| **Node 4** | **WEST** | `node4.mp4` | Follows Node 3 (Passes back to N) |

[You can download the test video from here!](https://drive.google.com/drive/folders/1d3Bcq2N8BO7fNCztuikJySmY1tocS9LR?usp=drive_link)
---

## 2. Prerequisites
* **Python 3.11** (Recommended)

### Installation
1. Open a terminal in the project folder.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt

---

## 3. How to Run the System

To simulate the distributed hardware, you must open **4 separate Terminal windows**.

### Step 1: Start Node 1 (North - The Leader)
Node 1 initializes the system and takes the first Green Light.

```bash
python vehicle_detection.py 1
```
Status: You will see "GREEN" and the timer counting down. The video will play.

### Step 2: Start Node 2 (East)
```bash
python vehicle_detection.py 2
```
Status: You will see "RED (Waiting)". The video will be frozen (simulating stopped traffic).

### Step 3: Start Node 3 (South)
```bash
python vehicle_detection.py 3
```
Status: "RED (Waiting)". Video frozen.

### Step 4: Start Node 4 (West)
```Bash
python vehicle_detection.py 4
```
Status: "RED (Waiting)". Video frozen.

Here is the complete, formatted content for your README.md file. It includes the header image, project overview, installation steps, and the specific running instructions you requested.

Markdown

# Smart Distributed Traffic Management System

![Smart Traffic Intersection Isometric View](https://img.freepik.com/free-vector/city-intersection-traffic-navigation-isometric-view_1284-17737.jpg?w=2000)

**A decentralized, AI-driven traffic control system using Computer Vision and Mesh Networking.**

This project implements a distributed traffic system where 4 separate camera nodes monitor a single intersection. Instead of a central server, the nodes communicate via a **Token Ring (Round Robin)** protocol to pass the "Green Light" authority efficiently in a cycle: **North → East → South → West**.

---

## 1. System Topology

Each Python instance represents one "Smart Camera" node monitoring a specific lane.

| Node ID | Direction | Video Source | Role |
| :--- | :--- | :--- | :--- |
| **Node 1** | **NORTH** | `node1.mp4` | **Leader** (Starts the system with the Green Token) |
| **Node 2** | **EAST** | `node2.mp4` | Follows Node 1 |
| **Node 3** | **SOUTH** | `node3.mp4` | Follows Node 2 |
| **Node 4** | **WEST** | `node4.mp4` | Follows Node 3 (Passes token back to Node 1) |


---

## 2. Prerequisites & Installation

* **Python 3.11** (Recommended)
* **Webcam** OR **4 Video Files** (for simulation)
  

### Installation
1. Clone the repository and open a terminal in the project folder.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
Setup Video Files
Ensure you have 4 video files in the project root folder named exactly as follows:

node1.mp4

node2.mp4

node3.mp4

node4.mp4

Note: If a file is missing, the system will attempt to open your webcam (0) instead.

3. How to Run the System
To simulate the distributed hardware, you must open 4 separate Terminal windows.

Step 1: Start Node 1 (North - The Leader)
Node 1 initializes the system and takes the first Green Light.
```python vehicle_detection.py 1```
Status: You will see "GREEN" and the timer counting down. The video will play.

Step 2: Start Node 2 (East)
```python vehicle_detection.py 2```
Status: You will see "RED (Waiting)". The video will be frozen (simulating stopped traffic).

Step 3: Start Node 3 (South)
```python vehicle_detection.py 3```
Status: "RED (Waiting)". Video frozen.

Step 4: Start Node 4 (West)
```python vehicle_detection.py 4```
Status: "RED (Waiting)". Video frozen.

### 4. What to Observe (The Demo Cycle)
Once all 4 nodes are running, the system will synchronize automatically. Watch the cycle flow:

1. Node 1 (North) counts cars → Calculates Green Time (e.g., 20s) → Timer Counts Down.

2. Node 1 turns YELLOW (3s) → sends TOKEN to Node 2.

3. Node 1 turns RED (Video Freezes).

4. Node 2 (East) receives Token → Instantly turns GREEN (Video Starts Playing).

5. Node 2 finishes → Passes to Node 3.

6. Node 3 finishes → Passes to Node 4.

7. Node 4 finishes → Passes back to Node 1.
