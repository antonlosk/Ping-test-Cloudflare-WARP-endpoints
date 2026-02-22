import subprocess
import re
import tkinter as tk
from tkinter import messagebox
from statistics import mean

def get_ips():
    """Generates the list of IP addresses based on the requested ranges."""
    ip_list = []
    
    # Range 162.159.192.1-20
    for i in range(1, 21):
        ip_list.append(f"162.159.192.{i}")
    
    # Range 162.159.195.1-10
    for i in range(1, 11):
        ip_list.append(f"162.159.195.{i}")
    
    return ip_list

def ping_ip(ip):
    """
    Pings an IP once and returns latency in ms.
    Returns None if the request timed out or failed.
    """
    # Windows ping command: -n 1 (count), -w 1000 (timeout in ms)
    command = ['ping', '-n', '1', '-w', '1000', ip]
    
    try:
        # We use encoding='cp866' to correctly read the command line output 
        # on Windows systems (handles both English and Russian system outputs).
        process = subprocess.run(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            encoding='cp866',
            errors='ignore' 
        ) 
        output = process.stdout
        
        # Regex to find the time. 
        # Looks for '=' or '<', followed by digits, followed by 'ms' (English) or 'мс' (Russian).
        match = re.search(r'[=<]\s*(\d+)\s*(ms|мс)', output, re.IGNORECASE)
        
        if match:
            latency = int(match.group(1))
            return latency
        else:
            return None
    except Exception as e:
        print(f"Script Error: {e}")
        return None

def main():
    print("=== Starting Ping Test ===")
    
    ips = get_ips()
    results = {} # Stores {ip: average_latency}

    total_ips = len(ips)
    
    for idx, ip in enumerate(ips):
        print(f"\n[{idx+1}/{total_ips}] Testing IP: {ip}")
        latencies = []
        
        for i in range(10):
            latency = ping_ip(ip)
            
            if latency is not None:
                print(f"  Ping {i+1}: {latency} ms")
                latencies.append(latency)
            else:
                print(f"  Ping {i+1}: Request Timed Out")
        
        # Calculate average only if we got at least one successful ping
        if latencies:
            avg_latency = mean(latencies)
            results[ip] = avg_latency
            print(f"  >> Average for {ip}: {avg_latency:.2f} ms")
        else:
            print(f"  >> No connection to {ip}")

    print("\n=== Testing Completed ===")

    # Sort results by lowest latency
    sorted_results = sorted(results.items(), key=lambda item: item[1])
    
    # Select Top 3
    top_3 = sorted_results[:3]
    
    # Prepare text for the popup window
    if top_3:
        msg_text = "Top 3 Fastest IPs (Average Latency):\n\n"
        for rank, (ip, avg) in enumerate(top_3, 1):
            msg_text += f"{rank}. {ip} — {avg:.2f} ms\n"
    else:
        msg_text = "No accessible IPs found."

    # Display the result window (Tkinter)
    root = tk.Tk()
    root.withdraw() # Hide the main root window
    root.attributes("-topmost", True) # Force window to stay on top
    messagebox.showinfo("Ping Test Results", msg_text)
    root.destroy()

if __name__ == "__main__":
    main()