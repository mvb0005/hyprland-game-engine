import socket
import os
import json
import subprocess
from typing import Any, List, Dict

class Hyprctl:
    def __init__(self):
        self.signature = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
        if not self.signature:
            # Fallback to finding it if not set (e.g. if run outside hyprland env explicitly)
            # But usually it is set.
            raise EnvironmentError("HYPRLAND_INSTANCE_SIGNATURE not found. Are you running inside Hyprland?")
        
        # Check XDG_RUNTIME_DIR first (modern Hyprland)
        xdg_runtime = os.environ.get("XDG_RUNTIME_DIR")
        if xdg_runtime:
            possible_path = f"{xdg_runtime}/hypr/{self.signature}/.socket.sock"
            if os.path.exists(possible_path):
                self.socket_path = possible_path
                return

        # Fallback to /tmp/hypr (legacy)
        self.socket_path = f"/tmp/hypr/{self.signature}/.socket.sock"
        
    def _send(self, command: str) -> str:
        """Send a raw command to the Hyprland socket."""
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
                client.connect(self.socket_path)
                client.sendall(command.encode('utf-8'))
                
                # Read response
                response = b""
                while True:
                    data = client.recv(4096)
                    if not data:
                        break
                    response += data
                    
                return response.decode('utf-8').strip()
        except FileNotFoundError:
             raise ConnectionError(f"Socket not found at {self.socket_path}")
        except Exception as e:
            raise ConnectionError(f"Failed to communicate with Hyprland socket: {e}")

    def run(self, command: str) -> str:
        # Legacy wrapper if needed, but we should prefer direct methods
        # Note: 'hyprctl command' maps to specific socket commands.
        # e.g. 'hyprctl dispatch ...' -> socket 'dispatch ...'
        # e.g. 'hyprctl -j clients' -> socket 'j/clients' (Wait, is it j/clients or clients with json flag?)
        
        # Hyprland Socket 1 (Control) protocol:
        # Just send the command string.
        # For JSON output, usually the command is different or flags are parsed.
        
        # 'hyprctl -j clients' actually sends 'j/clients' to the socket in recent versions?
        # Or just 'clients' and the socket returns a specific format?
        # Actually, looking at hyprctl source:
        # It sends "[flag]/[command]" sometimes.
        # -j flag usually means `j/` prefix for command.
        
        if command.startswith("-j"):
            # e.g. "-j clients" -> "j/clients"
            real_cmd = "j/" + command[3:].strip()
            return self._send(real_cmd)
        
        return self._send(command)

    def get_clients(self) -> List[Dict[str, Any]]:
        output = self.run("-j clients")
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            return []
            
    def dispatch(self, cmd: str) -> str:
        return self._send(f"dispatch {cmd}")
        
    def keyword(self, cmd: str) -> str:
        return self._send(f"keyword {cmd}")

    def batch(self, cmds: List[str]) -> str | None:
        """
        Run multiple commands in a single transaction using the batch command.
        Format: [[BATCH]]command1;command2;...
        """
        if not cmds:
            return None
            
        # Join with ; 
        joined = ";".join(cmds)
        
        # Send via socket using [[BATCH]] prefix which is the direct socket equivalent 
        # of `hyprctl --batch`.
        # Actually, `hyprctl --batch` just sends `[[BATCH]]cmd1;cmd2` to the socket.
        return self._send(f"[[BATCH]]{joined}")
