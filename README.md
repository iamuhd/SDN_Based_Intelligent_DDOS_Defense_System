# SDN_Based_Intelligent_DDOS_Defense_System
## 📌 Project Overview
System capable of accurately and promptly differentiating between sophisticated DDoS attack flows and legitimate traffic in an SDN environment. Current methods result in either unacceptable False Positives (blocking good traffic) or False Negatives (missing real attacks).This System utilizes **Machine Learning (Random Forest)** to dynamically analyze traffic behavior (Packet Rate, Byte Rate, Entropy) and autonomously block malicious hosts.

This system operates within a **Mininet** virtual environment, issuing OpenFlow commands to **Open vSwitch (OVS)** to physically isolate attackers while maintaining network availability for legitimate users.

![Python](https://img.shields.io/badge/Python-3.x-blue.svg) ![Mininet](https://img.shields.io/badge/Mininet-SDN-green.svg) ![Machine Learning](https://img.shields.io/badge/ML-Random%20Forest-orange.svg)


## 🚀 Key Features
* **🤖 AI-Driven Detection:** Uses a Random Forest Classifier to identify high-velocity DDoS attacks with high accuracy.
* **📊 Entropy-Based Analysis:** Calculates the randomness of source IP addresses to detect IP spoofing attempts.
* **🛡️ Reactive Mitigation:** Automatically pushes `drop` flow rules to the switch to block attackers in real-time.
* **💾 Persistence:** Maintains a `blocked_macs.json` registry to "remember" bad actors even after system restarts.
* **📈 Live Visualization:** Includes a "Sci-Fi" style dashboard (`visual_dashboard.py`) that renders real-time network traffic spikes.

## 🛠️ System Architecture
The system follows a cyclic lifecycle: **Collect → Train → Defend → Visualize**.

1.  **Infrastructure (`topo.py`):** Establishes the virtual network with 1 Switch and 6 Hosts.
2.  **Data Harvesting (`data_collector.py`):** Sniffs packets to extract features and generate a labeled dataset (`traffic_data.csv`).
3.  **Model Training (`train_model.py`):** Trains the Random Forest model and saves the "brain" as `ddos_model.pkl`.
4.  **Live Defense (`defense.py`):** The core script that monitors traffic, predicts attacks using the model, and bans attackers via OVS.
5.  **Monitoring (`visual_dashboard.py`):** Reads logs to display a live graph of network health.

## 💻 Technologies Used
| Component | Technology | File Reference |
| :--- | :--- | :--- |
| **OS** | Linux Ubuntu 20.04 (VirtualBox) | N/A |
| **Language** | Python 3 | All `.py` files |
| **Network Emulator** | Mininet | `topo.py` |
| **Switching/SDN** | Open vSwitch, OpenFlow | `defense.py` |
| **ML Engine** | Scikit-learn (Random Forest) | `train_model.py` |
| **Packet Sniffer** | Scapy | `data_collector.py` |
| **Visualization** | Matplotlib | `visual_dashboard.py` |
| **Data Handling** | Pandas, Joblib | `train_model.py` |


## ⚡ Installation & Usage

### Prerequisites
* Ubuntu 20.04 LTS (or similar Linux distro)
* Python 3.x
* Mininet
* Ryu Controller

### Step-by-Step Execution

1.  **Start the Controller**
    Launch the Ryu manager to handle OpenFlow switches:
    ```bash
    sudo ryu-manager ryu.app.simple_switch_13
    ```

2.  **Launch Network Topology**
    In a new terminal, start the Mininet environment:
    ```bash
    sudo python3 topo.py
    ```

3.  **Generate/Collect Data (Optional if model exists)**
    If you need to create a new dataset:
    ```bash
    sudo python3 data_collector.py
    ```

4.  **Train the Model**
    Train the Random Forest classifier on `traffic_data.csv`:
    ```bash
    python3 train_model.py
    ```

5.  **Start Defense System**
    Run the defense script to begin monitoring and mitigation:
    ```bash
    sudo python3 defense.py
    ```

6.  **Launch Dashboard**
    View real-time traffic statistics:
    ```bash
    python3 visual_dashboard.py
    ```

## 🧪 Testing
* **Normal Traffic:** Run `h1 ping h2` in the Mininet CLI. Result: No action.
* **DDoS Attack:** Run `h6 ping -f h1` (Ping Flood). Result: System detects high packet rate, blocks `h6`, and updates `blocked_macs.json`.

## 👥 Project Team
**Iqra University - Department of Computer Science (BS AI)**
* **Umair Hassan** (ID: 71371)
* **Xavier Rock** (ID: 71340)
* **Malik Faizan Ali** (ID: 71430)
* **Huzaifa Mehmood** (ID: 71333)

**Course:** Computer Network (CMC261)

This project was developed for academic purposes at Iqra University.
