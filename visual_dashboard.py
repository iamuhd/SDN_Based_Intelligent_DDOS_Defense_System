import matplotlib.pyplot as plt
import matplotlib.animation as animation
import re
import time

# SETTINGS
LOG_FILE = "traffic_log.txt"  # We will tell your defense script to write here

# Setup the Plot
fig, ax = plt.subplots()
xs = []
ys = []

def animate(i):
    try:
        # Read the latest speed from a temporary log file
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()
            if lines:
                last_line = lines[-1].strip()
                current_traffic = float(last_line)
            else:
                current_traffic = 0
    except:
        current_traffic = 0

    # Add to history
    xs.append(time.time())
    ys.append(current_traffic)
    
    # Keep only last 50 points
    if len(xs) > 50:
        xs.pop(0)
        ys.pop(0)

    # Draw
    ax.clear()
    ax.plot(xs, ys, color='cyan', linewidth=2)
    ax.fill_between(xs, ys, color='cyan', alpha=0.3)
    
    # Styling to look like a Sci-Fi Dashboard
    ax.set_facecolor('black')
    fig.patch.set_facecolor('black')
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.set_title("LIVE NETWORK TRAFFIC LOAD", color='white', fontsize=16)
    ax.set_ylabel("Packets Per Second", color='white')
    ax.grid(True, color='gray', linestyle='--', alpha=0.3)

# Create the file first so it doesn't crash
with open(LOG_FILE, "w") as f: f.write("0")

ani = animation.FuncAnimation(fig, animate, interval=500)
plt.show()
