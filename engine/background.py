import subprocess
import time

class BackgroundManager:
    def __init__(self, hyprctl, workspace=2):
        self.hyprctl = hyprctl
        self.workspace = workspace
        self.process = None
        self.address = None

    def set(self, image_path=None, color=None):
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
            # Make it huge to cover any screen
            subprocess.run(f"magick -size 3840x2160 xc:\"{color}\" {temp_bg}", shell=True)
            image_path = temp_bg
            
        cmd = ""
        if image_path:
            # imv command: imv -f (fullscreen) is not what we want if we want it tiled?
            # Actually, if we spawn it tiled, it fills the space.
            # We just need it to open the file.
            # imv doesn't have a --class flag easily? 
            # We can use `imv-wayland`? Or just `imv`.
            # We rely on window rules to catch it.
            # IMV usually has class "imv". We can't easily change it.
            # So we must use "class:imv" rule.
            
            cmd = f"imv {image_path}"
            bg_class = "imv" 
        else:
            # Fallback to black image if nothing provided
            subprocess.run(f"magick -size 1920x1080 xc:\"#000000\" /tmp/game_bg_black.png", shell=True)
            cmd = f"imv /tmp/game_bg_black.png"
            bg_class = "imv"
            
        # Atomic spawn using exec [rules]
        self.hyprctl.keyword(f"workspace {self.workspace},gapsin:0,gapsout:0")
        rules = f"workspace {self.workspace} silent;noanim"
        
        # IMPORTANT: imv might exit if we don't keep it open? 
        # By default imv stays open until closed.
        
        real_cmd = f"hyprctl dispatch exec \"[{rules}]\" \"{cmd}\""
        print(f"Direct Spawn (IMV): {real_cmd}")
        subprocess.run(real_cmd, shell=True)
        
        time.sleep(0.5)
        
        # Find it
        # We might need to retry finding it if it spawns slowly
        clients = []
        for attempt in range(10):
            clients = self.hyprctl.get_clients()
            for client in clients:
                if bg_class in client.get('class', ''):
                    if client['workspace']['id'] == self.workspace:
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
            # Let's set it to something huge to be safe, or 2560.
            
            width = 2560
            height = 1440 
            
            self.hyprctl.dispatch(f"resizeactive exact {width} {height} address:{self.address}")
            self.hyprctl.dispatch(f"moveactive exact 0 0 address:{self.address}")
            
            # Use 'alterzorder' to push it to the bottom?
            # 'dispatch alterzorder bottom,address:X'
            self.hyprctl.dispatch(f"alterzorder bottom,address:{self.address}")
            
            # If we can't tile it, we just accept it's a floating window at the back.
            # The danger is if the user clicks it, it might obscure others.
            # But we can set 'xray 1'? No.
            
            # Actually, let's try 'pin' ? No, pin makes it show on all workspaces.
            
            # Best bet for "floating background":
            # 1. Fullscreen it (this usually keeps it below other floating windows if they are focused?)
            #    No, fullscreen takes over.
            # 2. Maximize (Fullscreen 1) - keeps bars visible (we have none) and allows other floating windows on top?
            #    Let's try Fullscreen 1 (Maximize) again, but ensuring we push it to bottom first.
            
            self.hyprctl.dispatch(f"fullscreen 1 address:{self.address}")
            
            # Re-apply z-order push just in case
            self.hyprctl.dispatch(f"alterzorder bottom,address:{self.address}")
            
    def cleanup(self):
        if self.process:
            self.process.terminate()
        if self.address:
            self.hyprctl.dispatch(f"closewindow address:{self.address}")
