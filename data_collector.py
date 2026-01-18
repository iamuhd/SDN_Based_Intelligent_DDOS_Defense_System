import pandas as pd
from scapy.all import sniff
from collections import defaultdict
import math
import time
import os

# --- CONFIGURATION ---
WINDOW_SIZE = 1
INTERFACE = "s1-eth1"
CSV_FILE = "traffic_data.csv"

# --- GLOBAL VARIABLES ---
pkt_count = 0
byte_count = 0
ip_src_counts = defaultdict(int)

def calculate_entropy(ip_counts):
    total_packets = sum(ip_counts.values())
    if total_packets == 0:
        return 0
    entropy = 0
    for count in ip_counts.values():
        p = count / total_packets
        entropy -= p * math.log2(p)
    return entropy

def process_packet(packet):
    global pkt_count, byte_count, ip_src_counts
    pkt_count += 1
    byte_count += len(packet)
    if packet.haslayer('IP'):
        src_ip = packet['IP'].src
        ip_src_counts[src_ip] += 1

def monitor_loop():
    global pkt_count, byte_count, ip_src_counts
    
    # Create file with header if it doesn't exist
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=["pkt_rate", "byte_rate", "entropy", "label"])
        df.to_csv(CSV_FILE, index=False)
        print(f"[*] Created new file: {CSV_FILE}")

    print(f"[*] Monitoring started... Auto-saving to {CSV_FILE}")

    while True:
        try:
            sniff(iface=INTERFACE, prn=process_packet, timeout=WINDOW_SIZE, store=0)
            
            entropy = calculate_entropy(ip_src_counts)
            label = 1  # 0 = Normal 1 = Attack
            
            # Print to screen
            print(f"Rate: {pkt_count} | Entropy: {entropy:.2f} | Saved: YES")
            
            # SAVE INSTANTLY
            data = {
                "pkt_rate": [pkt_count],
                "byte_rate": [byte_count],
                "entropy": [entropy],
                "label": [label]
            }
            df = pd.DataFrame(data)
            df.to_csv(CSV_FILE, mode='a', header=False, index=False)
            
            # Reset
            pkt_count = 0
            byte_count = 0
            ip_src_counts.clear()
            
        except KeyboardInterrupt:
            print("\n[!] User stopped the script.")
            break

if __name__ == "__main__":
    monitor_loop()
