import subprocess
import time

class WindowManager:
    def __init__(self, hyprctl, workspace=2):
        self.hyprctl = hyprctl
        self.workspace = workspace
        self.windows = []
        self.processes = []

    def spawn_batch(self, windows_config):
        """
        Spawn multiple windows at once using hyprctl batching with exec rules.
        windows_config: List of dicts with keys: command, name_pattern, x, y, width, height, is_class
        """
        print(f"Batch spawning {len(windows_config)} windows...")
        
        batch_cmds = []
        import os
        conf_path = os.path.expanduser("~/code/games/ghostty_game.conf")

        for cfg in windows_config:
            # Prepare command
            cmd = cfg['command']
            if "ghostty" in cmd and "--config-file" not in cmd:
                 cmd = cmd.replace("ghostty", f"ghostty --config-file={conf_path}")
            
            # Prepare rules
            # Note: Rules in exec syntax are [rule1;rule2;...]
            # We enforce workspace 2, float, noanim, size, move
            rules = [
                f"workspace {self.workspace} silent",
                "float",
                "noanim",
                f"size {cfg['width']} {cfg['height']}",
                f"move {cfg['x']} {cfg['y']}"
            ]
            rule_str = ";".join(rules)
            
            # Construct dispatch command
            # Hyprland exec syntax: dispatch exec [rules] command
            # batch_cmds.append(f"dispatch exec [{rule_str}] {cmd}")
            
            # We cannot use hyprctl --batch here because the rules inside [] use semicolons
            # which conflict with the batch separator.
            # So we execute them individually.
            
            # Important: Quote the rule block so shell/hyprctl handles spaces correctly
            # and quote the command part too.
            full_cmd = f"exec \"[{rule_str}]\" \"{cmd}\""
            print(f"Dispatching: {full_cmd}")
            self.hyprctl.dispatch(full_cmd)
            
        # print("Launching windows via batch exec...")
        # self.hyprctl.batch(batch_cmds)

        # 3. Wait for ALL windows (Polling)
        # We need the addresses to manage them later (close, etc)
        found_windows = {} # index -> address
        retries = 50
        while retries > 0 and len(found_windows) < len(windows_config):
            clients = self.hyprctl.get_clients()
            
            for i, cfg in enumerate(windows_config):
                if i in found_windows: continue
                
                pattern = cfg['name_pattern']
                is_class = cfg.get('is_class', False)
                
                for client in clients:
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
        for i, addr in found_windows.items():
            self.windows.append({
                "address": addr,
                "proc": None # We don't have PIDs for hyprctl exec spawned processes easily
            })
            
        if len(found_windows) < len(windows_config):
            print(f"Warning: Only found {len(found_windows)}/{len(windows_config)} windows.")

    def spawn(self, command, name_pattern, x, y, width, height, is_class=True):
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

    def cleanup(self):
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

    def close_matching(self, patterns):
        """
        Close any window (owned or not) that matches the given patterns.
        Useful for cleaning up leftovers from previous sessions.
        """
        print(f"Scanning for leftover windows matching: {patterns}")
        clients = self.hyprctl.get_clients()
        to_close = []
        
        for client in clients:
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
