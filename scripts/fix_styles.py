
import sys
import os
import json
import subprocess

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def main():
    print("Scanning Workspace 1 for windows to reset...")
    try:
        clients_json = run_cmd("hyprctl -j clients")
        clients = json.loads(clients_json)
        
        ws1_clients = [c for c in clients if c['workspace']['id'] == 1]
        
        if not ws1_clients:
            print("No windows found on Workspace 1.")
            return

        print(f"Found {len(ws1_clients)} windows. Resetting properties...")
        
        for c in ws1_clients:
            addr = c['address']
            title = c.get('title', 'Unknown')
            print(f"Resetting: {title} ({addr})")
            
            # Revert 'noborder' (0 = show border / obey config)
            run_cmd(f"hyprctl dispatch setprop address:{addr} noborder 0")
            
            # Revert 'rounding' (-1 = use config default)
            run_cmd(f"hyprctl dispatch setprop address:{addr} rounding -1")
            
            # Revert 'noshadow' (0 = show shadow)
            run_cmd(f"hyprctl dispatch setprop address:{addr} noshadow 0")
            
            # Revert 'noblur' (0 = enable blur)
            run_cmd(f"hyprctl dispatch setprop address:{addr} noblur 0")
            
            # Revert 'noanim' (0 = enable animations)
            run_cmd(f"hyprctl dispatch setprop address:{addr} noanim 0")

        print("Done. Window styles should be restored.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
