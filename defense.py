import os
import sys
import time
import math
import joblib
import json  # <--- Added for saving data
import pandas as pd
import threading
from scapy.all import sniff, IP, Ether, ICMP, TCP
from collections import defaultdict, deque

# --- CONFIGURATION ---
INTERFACE = ["s1-eth1", "s1-eth2", "s1-eth3", "s1-eth4", "s1-eth5", "s1-eth6"]
MODEL_FILE = "ddos_model.pkl"
BLOCK_FILE = "blocked_macs.json"  # <--- The memory file
WINDOW_SIZE = 0.8
BLOCK_THRESHOLD = 40

# --- GLOBAL VARIABLES ---
pkt_count = 0
attack_score = defaultdict(int)
blocked_macs = set()
logs = deque(maxlen=8)
current_status = "INITIALIZING..."
stop_threads = False
pause_monitor = False

# --- PERSISTENCE FUNCTIONS (MEMORY) ---
def load_blocks():
    """Reads the blocked list from file on startup."""
    if not os.path.exists(BLOCK_FILE):
        return set()
    try:
        with open(BLOCK_FILE, 'r') as f:
            data = json.load(f)
            return set(data)
    except:
        return set()

def save_blocks():
    """Saves the current blocked list to file."""
    try:
        with open(BLOCK_FILE, 'w') as f:
            json.dump(list(blocked_macs), f)
    except Exception as e:
        print(f"[!] Error saving blocks: {e}")

# --- HELPER FUNCTIONS ---
def calculate_entropy(ip_counts):
    total = sum(ip_counts.values())
    if total == 0: return 0
    entropy = 0
    for count in ip_counts.values():
        p = count / total
        entropy -= p * math.log2(p)
    return entropy

def block_attacker(mac):
    """Blocks and Saves to file."""
    mac = mac.lower()
    if mac in blocked_macs: return False
    
    logs.append(f"[!!!] BLOCKING AGGRESSOR: {mac}")
    os.system(f"sudo ovs-ofctl add-flow s1 priority=1000,dl_src={mac},actions=drop")
    os.system("sudo ovs-appctl revalidator/purge")
    
    blocked_macs.add(mac)
    save_blocks()  # <--- SAVE INSTANTLY
    return True

def unblock_attacker(mac):
    mac = mac.lower()
    if mac not in blocked_macs: 
        print(f"[-] MAC {mac} is not currently blocked.")
        return
    print(f"[*] Unblocking {mac}...")
    os.system(f"sudo ovs-ofctl del-flows s1 dl_src={mac}")
    os.system("sudo ovs-appctl revalidator/purge")
    blocked_macs.remove(mac)
    save_blocks()  # <--- UPDATE FILE
    logs.append(f"[*] UNBLOCKED: {mac}")

# --- PACKET PROCESSING ---
def process_packet(packet):
    global pkt_count
    pkt_count += 1
    
    if packet.haslayer(Ether):
        src_mac = packet[Ether].src
        
        # Ignore already blocked MACs to save CPU
        if src_mac in blocked_macs: return

        # --- SMART FILTER ---
        if packet.haslayer(ICMP):
            if packet[ICMP].type == 8: 
                attack_score[src_mac] += 1
            elif packet[ICMP].type == 0: 
                return 
        elif packet.haslayer(TCP):
            flags = packet[TCP].flags
            if 'S' in flags and 'A' not in flags: 
                attack_score[src_mac] += 1
            else:
                return 
        else:
            attack_score[src_mac] += 1

# --- MONITORING THREAD ---
def packet_monitor():
    global pkt_count, current_status
    
    while not stop_threads:
        while pause_monitor:
            current_status = "⏸️  MANAGER MENU OPEN"
            time.sleep(0.5)
            if stop_threads: return

        pkt_count = 0
        attack_score.clear()

        sniff(iface=INTERFACE, prn=process_packet, timeout=WINDOW_SIZE, store=0)

        normalized_rate = pkt_count / WINDOW_SIZE
        
        # Fixed indentation for file writing
        with open("traffic_log.txt", "w") as f:
            f.write(str(normalized_rate))    
        
        max_attacker = None
        max_score = 0
        for mac, score in attack_score.items():
            if score > max_score:
                max_score = score
                max_attacker = mac
        
        max_score_rate = max_score / WINDOW_SIZE

        if max_score_rate > BLOCK_THRESHOLD:
            current_status = "⚠️  ATTACK IN PROGRESS ⚠️"
            logs.append(f"ALERT: {max_attacker} @ {max_score_rate:.0f} pps")
            
            if block_attacker(max_attacker):
                current_status = "⚠️  ATTACK IN PROGRESS ⚠️"
                draw_dashboard(normalized_rate, max_score_rate)
                time.sleep(2.0) 
                continue 
        else:
            current_status = "✅  SYSTEM SECURE"

        if not pause_monitor:
            draw_dashboard(normalized_rate, max_score_rate)

# --- DASHBOARD ---
def draw_dashboard(rate, max_attack_score):
    os.system('clear')
    print("="*60)
    print(f"       🛡️  SMART DDOS ATTACK DEFENSE SYSTEM  🛡️  ")
    print("="*60)
    print(f"\nSTATUS:  {current_status}")
    print(f"TRAFFIC: {rate:.0f} pps")
    print(f"THREAT:  {max_attack_score:.0f} malicious pps")
    
    print("\n" + "-"*60)
    print(f"BLOCKED ATTACKERS :")
    print("-"*60)
    if not blocked_macs:
        print("  (None)")
    else:
        for mac in blocked_macs:
            print(f"  🛑 {mac}")

    print("\n" + "-"*60)
    print("LOGS:")
    print("-"*60)
    for log in logs:
        print(f"  > {log}")
    
    print("\n" + "="*60)
    print("Press [Ctrl+C] for Menu")

def show_menu():
    global pause_monitor, stop_threads
    pause_monitor = True
    time.sleep(1)
    
    while True:
        os.system('clear')
        print("="*50)
        print("      ⏸️  MANAGER MENU  ⏸️")
        print("="*50)
        print("\nOPTIONS:")
        print(" [1] Unblock MAC")
        print(" [2] Clear All Blocks")
        print(" [3] Resume")
        print(" [4] Quit")
        
        choice = input("\nSelect: ")
        
        if choice == '1':
            target = input("Enter MAC: ")
            unblock_attacker(target.strip())
            input("Press Enter...")
        elif choice == '2':
            for m in list(blocked_macs): unblock_attacker(m)
            input("Press Enter...")
        elif choice == '3':
            pause_monitor = False
            break
        elif choice == '4':
            stop_threads = True
            pause_monitor = False
            sys.exit(0)

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("Run as sudo.")
        sys.exit(1)

    # 1. Reset Switch (Wipes everything)
    os.system("ovs-ofctl del-flows s1")
    os.system("ovs-ofctl add-flow s1 priority=0,actions=normal")
    
    # 2. LOAD SAVED BLOCKS
    print(f"[*] Checking for saved blocks in {BLOCK_FILE}...")
    saved_macs = load_blocks()
    blocked_macs = saved_macs # Sync memory
    
    if len(saved_macs) > 0:
        print(f"[*] Restoring {len(saved_macs)} blocked attackers...")
        for mac in saved_macs:
            print(f"    -> Re-blocking {mac}")
            os.system(f"sudo ovs-ofctl add-flow s1 priority=1000,dl_src={mac},actions=drop")
    else:
        print("[*] No previous blocks found.")

    if not os.path.exists(MODEL_FILE):
        print("Model not found.")
        sys.exit(1)
    
    loaded_model = joblib.load(MODEL_FILE)
    
    t = threading.Thread(target=packet_monitor, daemon=True)
    t.start()
    
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            show_menu()
