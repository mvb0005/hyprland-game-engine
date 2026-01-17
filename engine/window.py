import subprocess
import time
from typing import List, Dict, Any, Optional
from .core import Hyprctl

class WindowManager:
    def __init__(self, hyprctl: Hyprctl, workspace: int = 2):
        self.hyprctl = hyprctl
        self.workspace = workspace
        self.windows: List[Dict[str, Any]] = []
        self.processes: List[subprocess.Popen] = []

    def spawn_batch(self, windows_config: List[Dict[str, Any]]) -> None:
        """
        Spawn multiple windows at once using hyprctl batching with exec rules.
        windows_config: List of dicts with keys: command, name_pattern, x, y, width, height, is_class
        """
        print(f"Batch spawning {len(windows_config)} windows...")
        
        # batch_cmds = []
        import os
        conf_path = os.path.expanduser("~/code/games/ghostty_game.conf")

        spawn_cmds = []
        for cfg in windows_config:
            # Prepare command
            cmd = cfg['command']
            if "ghostty" in cmd and "--config-file" not in cmd and "--config" not in cmd:
                 cmd = cmd.replace("ghostty", f"ghostty --config-file={conf_path}")
            
            # Prepare rules
            # Note: Rules in exec syntax are [rule1;rule2;...]
            # We enforce workspace 2, float, custom animation, size, move
            anim_rule = "animation popin 80%"
            if "KeyHandler" in cfg['name_pattern']:
                anim_rule = "noanim"
                
            rules = [
                f"workspace {self.workspace} silent",
                "float",
                anim_rule, # Custom animation style or none
                "noshadow",
                "noborder",
                "norounding",
                "noblur",
                f"size {cfg['width']} {cfg['height']}",
                f"move {cfg['x']} {cfg['y']}"
            ]

            rule_str = ";".join(rules)
            
            # Construct dispatch command
            # Hyprland exec syntax: dispatch exec [rules] command
            
            # We cannot use hyprctl --batch here because the rules inside [] use semicolons
            # which conflict with the batch separator.
            # So we execute them individually.
            
            # Important: Quote the rule block so shell/hyprctl handles spaces correctly
            # and quote the command part too.
            # UPDATE: Hyprland socket does NOT want quotes around the command or rules!
            full_cmd = f"exec [{rule_str}] {cmd}"
            # print(f"Dispatching: {full_cmd}")
            self.hyprctl.dispatch(full_cmd)
            spawn_cmds.append(full_cmd)
            
        if spawn_cmds:
            print(f"Dispatched {len(spawn_cmds)} windows...")
            # self.hyprctl.batch(spawn_cmds)
            
        # 3. Wait for ALL windows (Polling)
        # We need the addresses to manage them later (close, etc)
        # found_windows maps index (in windows_config) -> address (str)
        found_windows = {} 
        retries = 50
        while retries > 0 and len(found_windows) < len(windows_config):
            clients = self.hyprctl.get_clients()
            
            for i, cfg in enumerate(windows_config):
                if i in found_windows: continue
                
                pattern = cfg['name_pattern']
                is_class = cfg.get('is_class', False)
                
                for client in clients:
                    # STRICT CHECK: Only consider windows on the target workspace
                    # This prevents us from grabbing (and resizing) a user's terminal/editor on Workspace 1
                    # that happens to have a matching title (e.g. "BoggleBoard.py - Vim")
                    if client['workspace']['id'] != self.workspace:
                        continue

                    match_found = False
                    if is_class:
                        if pattern in client.get('class', ''): match_found = True
                    else:
                        if pattern in client.get('title', '') or pattern in client.get('initialTitle', ''): match_found = True
                    
                    if match_found:
                        # Ensure uniqueness
                        if client['address'] not in [w['address'] for w in self.windows] and client['address'] not in found_windows.values():
                            found_windows[i] = client['address']
                            break
            
            if len(found_windows) == len(windows_config):
                break
            time.sleep(0.1)
            retries -= 1

        # 4. Register found windows
        # print(f"DEBUG: found_windows type: {type(found_windows)}")
        if isinstance(found_windows, list):
             # Fallback if somehow it became a list (should not happen)
             # Convert to dict logic or just handle it
             print("Error: found_windows became a list!")
             # Try to recover?
             found_windows = {i: addr for i, addr in enumerate(found_windows)}

        for i, addr in found_windows.items():
            self.windows.append({
                "address": addr,
                "proc": None # We don't have PIDs for hyprctl exec spawned processes easily
            })
            
        # 5. Enforce Geometry (Fix for spawning on inactive workspace)
        # Sometimes exec rules (move/size) are ignored if the workspace is not active.
        # We explicitly move/resize them now that we have their addresses.
        geometry_cmds = []
        for i, addr in found_windows.items():
            cfg = windows_config[i]
            # Force floating state to ensure it sits above the background and respects size/move
            # Tiled windows (floating: false) are rendered behind floating windows (like our background)
            geometry_cmds.append(f"dispatch setfloating address:{addr}")
            
            # Explicitly disable fullscreen if it was auto-enabled (common with Chromium --app)
            geometry_cmds.append(f"dispatch fullscreen 0 address:{addr}")
            
            # Chromium specific transparency? Hyprland can set opacity.
            # If it's the Join window, maybe make it slightly transparent to blend if needed?
            # But the HTML has a background color.
            # Actually user asked for QR in bottom right corner.
            # If we make the window transparent, we can overlay it?
            # Chromium doesn't support transparent background easily.
            # We rely on the CSS styling we just added.
            
            # Syntax: resizewindowpixel exact W H,address:ADDR
            geometry_cmds.append(f"dispatch resizewindowpixel exact {cfg['width']} {cfg['height']},address:{addr}")
            # Syntax: movewindowpixel exact X Y,address:ADDR
            geometry_cmds.append(f"dispatch movewindowpixel exact {cfg['x']} {cfg['y']},address:{addr}")
            
        if geometry_cmds:
            print(f"Enforcing geometry (and floating) for {len(geometry_cmds)//3} windows...")
            self.hyprctl.batch(geometry_cmds)

        if len(found_windows) < len(windows_config):
            print(f"Warning: Only found {len(found_windows)}/{len(windows_config)} windows.")

    def spawn(self, command: str, name_pattern: str, x: int, y: int, width: int, height: int, is_class: bool = True) -> Optional[Dict[str, Any]]:
        """
        Spawn a single window using exec rules.
        """
        # Wrap as single item batch
        cfg = {
            "command": command,
            "name_pattern": name_pattern,
            "x": x, "y": y,
            "width": width, "height": height,
            "is_class": is_class
        }
        self.spawn_batch([cfg])
        
        # Return the last added window
        if self.windows:
            return self.windows[-1]
        return None

    def cleanup(self) -> None:
        print("Cleaning up windows...")
        # Since we don't have procs, we rely entirely on Hyprland closewindow
        # batching the closes for speed
        if not self.windows:
            return
            
        close_cmds = [f"dispatch closewindow address:{w['address']}" for w in self.windows]
        if close_cmds:
            self.hyprctl.batch(close_cmds)
        self.windows = []
        self.processes = []

    def close_matching(self, patterns: List[str]) -> None:
        """
        Close any window (owned or not) that matches the given patterns.
        Useful for cleaning up leftovers from previous sessions.
        """
        print(f"Scanning for leftover windows matching: {patterns}")
        clients = self.hyprctl.get_clients()
        to_close = []
        
        for client in clients:
            # STRICT CHECK: Only close windows on the target workspace
            # This protects the user's other workspaces (e.g. Workspace 1)
            if client['workspace']['id'] != self.workspace:
                continue

            matched = False
            for p in patterns:
                # Check title, initialTitle, and class
                if (p in client.get('title', '') or 
                    p in client.get('initialTitle', '') or 
                    p in client.get('class', '')):
                    matched = True
                    break
            
            if matched:
                print(f"Found leftover window: {client.get('title')} ({client['address']})")
                to_close.append(f"dispatch closewindow address:{client['address']}")
                
        if to_close:
            print(f"Closing {len(to_close)} leftover windows...")
            self.hyprctl.batch(to_close)
