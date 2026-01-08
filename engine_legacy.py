import subprocess
import json
import time
import os
import sys

class HyprlandEngine:
    def __init__(self, target_workspace=2):
        self.workspace = target_workspace
        self.processes = []
        self.windows = []
        # Removed system-level background handling

    def run_hyprctl(self, command):
        """Run a raw hyprctl command."""
        cmd = f"hyprctl {command}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip()

    def get_clients(self):
        """Get all clients as JSON."""
        output = self.run_hyprctl("-j clients")
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            return []

    def switch_to_workspace(self):
        """Switch view to the game workspace."""
        print(f"Switching to workspace {self.workspace}...")
        self.run_hyprctl(f"dispatch workspace {self.workspace}")

    def clear_workspace(self):
        """Close all windows on the target workspace."""
        print(f"Clearing workspace {self.workspace}...")
        clients = self.get_clients()
        for client in clients:
            if client['workspace']['id'] == self.workspace:
                self.run_hyprctl(f"dispatch closewindow address:{client['address']}")

    def set_background(self, image_path=None, color=None):
        """
        Spawn a fullscreen window on the game workspace to act as a background.
        Args:
            image_path: Path to an image file.
            color: Hex color string (e.g. '#000000'). Used if image_path is None.
        """
        print(f"Spawning background window...")
        
        cmd = ""
        if image_path:
             # Use imv for images
            cmd = f"imv -f {image_path}"
        elif color:
            # Use a terminal with a solid background color as a hack
            cmd = f"ghostty --title=GameBackground --background={color} -e sh -c 'sleep infinity'"
        else:
            cmd = "ghostty --title=GameBackground --background=#000000 -e sh -c 'sleep infinity'"
            
        # Spawn the background window
        proc = subprocess.Popen(cmd, shell=True)
        self.processes.append(proc)
        
        time.sleep(0.5) # Give it a moment
        
        # Find it
        bg_address = None
        clients = self.get_clients()
        for client in clients:
            if "GameBackground" in client['title'] or "imv" in client['class']:
                 bg_address = client['address']
                 break
        
        if bg_address:
            print(f"Configuring background window {bg_address}...")
            # Move to workspace
            self.run_hyprctl(f"dispatch movetoworkspacesilent {self.workspace},address:{bg_address}")
            
            # Stick to Tiled Background + Floating UI logic
            self.run_hyprctl(f"dispatch setprop address:{bg_address} noborder 1")
            self.run_hyprctl(f"dispatch setprop address:{bg_address} rounding 0")
            
            # Force it to tile
            self.run_hyprctl(f"dispatch tile address:{bg_address}")
            self.run_hyprctl(f"dispatch fullscreen 1 address:{bg_address}")

    def restore_background(self):
        """No-op: Background window dies with cleanup."""
        pass

    def spawn_window(self, command, title_pattern, x, y, width, height, app_id=None):
        """
        Spawn a window and position it.
        """
        print(f"Spawning: {command}")
        
        # PRE-OPTIMIZATION: Add a temporary windowrule to force this specific window to float immediately
        # This prevents the "tiled then float" jump animation
        self.run_hyprctl(f"keyword windowrule float,title:^({title_pattern})$")
        self.run_hyprctl(f"keyword windowrule noanim,title:^({title_pattern})$") # Optional: disable entry animation
        
        # Launch process in background
        proc = subprocess.Popen(command, shell=True)
        self.processes.append(proc)

        # Wait for window to appear
        address = None
        retries = 50 # 5 seconds
        while retries > 0:
            clients = self.get_clients()
            for client in clients:
                # Check match
                if title_pattern in client['initialTitle'] or title_pattern in client['title'] or (app_id and app_id in client['class']):
                    # Ensure it's not a window we already grabbed (naive check)
                    if client['address'] not in [w['address'] for w in self.windows]:
                        address = client['address']
                        break
            
            if address:
                break
            time.sleep(0.1)
            retries -= 1

        if not address:
            print(f"Failed to find window for {title_pattern}")
            return None

        print(f"Found window {address}. Configuring...")
        
        # Move to workspace (if not already there)
        self.run_hyprctl(f"dispatch movetoworkspacesilent {self.workspace},address:{address}")
        
        # Float it (should already be float due to windowrule, but ensure it)
        self.run_hyprctl(f"dispatch togglefloating address:{address}")
        self.run_hyprctl(f"dispatch setfloating address:{address}")
        
        # Position and Resize
        self.run_hyprctl(f"dispatch resizeactive exact {width} {height} address:{address}")
        self.run_hyprctl(f"dispatch moveactive exact {x} {y} address:{address}")
        
        window_obj = {
            "address": address,
            "proc": proc
        }
        self.windows.append(window_obj)
        return window_obj

    def cleanup(self):
        """Kill all spawned processes."""
        print("Cleaning up...")
        
        self.restore_background()

        for p in self.processes:
            p.terminate()
        # Also close the windows specifically
        for w in self.windows:
            self.run_hyprctl(f"dispatch closewindow address:{w['address']}")

if __name__ == "__main__":
    # Simple test if run directly
    engine = HyprlandEngine()
    engine.switch_to_workspace()
