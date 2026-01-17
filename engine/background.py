import subprocess
import time
from typing import Optional, List, Dict, Any
from .core import Hyprctl

class BackgroundManager:
    def __init__(self, hyprctl: Hyprctl, workspace: int = 2):
        self.hyprctl = hyprctl
        self.workspace = workspace
        self.process: Optional[subprocess.Popen] = None
        self.address: Optional[str] = None

    def set(self, image_path: Optional[str] = None, color: Optional[str] = None) -> None:
        print(f"Spawning background window...")
        
        # Using a distinct class for the background to ensure we can rule-match it easily if needed
        bg_class = "GameBackground"
        
        # If color is provided but no image, generate a temp image for IMV
        # Ghostty was showing cursor, IMV is better for static images.
        if color and not image_path:
            # Requires ImageMagick
            import os
            temp_bg = "/tmp/game_bg_generated.png"
            # 1x1 pixel is enough if we scale it, but safer to make it decent size?
            # IMV scales up by default usually.
            # Get monitor resolution dynamically
            width = 2048 # Default
            height = 1080 # Default
            try:
                monitors = self.hyprctl.get_clients() # Wait, get_clients is wrong, need get_monitors logic
                # self.hyprctl.run("-j monitors") returns the json string
                import json
                mon_json = json.loads(self.hyprctl.run("-j monitors"))
                if mon_json:
                    # Use the first focused monitor or just the first one
                    m = mon_json[0]
                    for x in mon_json:
                        if x.get('focused'): m = x; break
                    
                    # Calculate logical size
                    scale = m.get('scale', 1)
                    width = int(m['width'] / scale)
                    height = int(m['height'] / scale)
                    print(f"Detected Monitor Resolution: {width}x{height}")
            except Exception as e:
                print(f"Error detecting resolution: {e}. Using default 2048x1080")

            # Match monitor aspect ratio and size
            subprocess.run(f"magick -size {width}x{height} xc:\"{color}\" {temp_bg}", shell=True)
            image_path = temp_bg
            
        cmd = ""
        if image_path:
            # Use imv with crop scaling to cover the window without black bars
            cmd = f"imv -s crop {image_path}"
            bg_class = "imv" 
        else:
            # Fallback to black image
            subprocess.run(f"magick -size {width}x{height} xc:\"#000000\" /tmp/game_bg_black.png", shell=True)
            cmd = f"imv -s crop /tmp/game_bg_black.png"
            bg_class = "imv"
            
        # Atomic spawn using exec [rules]
        # self.hyprctl.keyword(f"workspace {self.workspace},gapsin:0,gapsout:0")
        rules = f"workspace {self.workspace} silent;noanim"
        
        # IMPORTANT: imv might exit if we don't keep it open? 
        # By default imv stays open until closed.
        
        # real_cmd = f"hyprctl dispatch exec \"[{rules}]\" \"{cmd}\""
        # print(f"Direct Spawn (IMV): {real_cmd}")
        # subprocess.run(real_cmd, shell=True)
        
        # Batch the workspace config and the spawn
        batch_cmds = [
            f"keyword workspace {self.workspace},gapsin:0,gapsout:0",
            f"dispatch exec [{rules}] {cmd}"
        ]
        print(f"Batch Spawning Background: {batch_cmds}")
        self.hyprctl.batch(batch_cmds)
        
        time.sleep(0.5)
        
        # Find it
        # We might need to retry finding it if it spawns slowly
        clients: List[Dict[str, Any]] = []
        for attempt in range(10):
            clients = self.hyprctl.get_clients()
            for client in clients:
                if bg_class in client.get('class', ''):
                    if client.get('workspace', {}).get('id') == self.workspace:
                        self.address = client['address']
                        break
            if self.address:
                break
            time.sleep(0.2)
        
        if self.address:
            print(f"Configuring background window {self.address}...")
            # Remove borders and rounding
            self.hyprctl.dispatch(f"setprop address:{self.address} noborder 1")
            self.hyprctl.dispatch(f"setprop address:{self.address} rounding 0")
            
            # Alternative Strategy: Keep it FLOATING, but size it to full screen
            # and potentially pin it or just leave it.
            # Hyprland draws floating windows on top of tiled ones.
            # But amongst floating windows, the active one is on top.
            # If we click the background, it might come to front.
            
            # We can use `setprop` to force negative z-order? No such prop.
            # But we CAN just resize it to match the monitor.
            
            # Get monitor resolution? We assume 1920x1080 for now or fetch it.
            # Let's hardcode 1920x1080 for the demo as used elsewhere.
            # UPDATE: User reported it doesn't go to the right edge.
            # We likely have a wider monitor (2560x1080 or 1440p?).
            # Set to exact logical resolution of the monitor
            # width = 2048
            # height = 1080
            # We already calculated width/height above, use those variables
            
            self.hyprctl.batch([
                f"dispatch resizewindowpixel exact {width} {height},address:{self.address}",
                f"dispatch movewindowpixel exact 0 0,address:{self.address}",
                f"dispatch focuswindow address:{self.address}",
                "dispatch alterzorder bottom",
                "dispatch fullscreen 1",
                "dispatch alterzorder bottom"
            ])
            
    def cleanup(self) -> None:
        if self.process:
            self.process.terminate()
        if self.address:
            self.hyprctl.dispatch(f"closewindow address:{self.address}")
