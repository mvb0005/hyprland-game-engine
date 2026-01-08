import subprocess
import json
from typing import Any, List, Dict

class Hyprctl:
    def run(self, command: str) -> str:
        cmd = f"hyprctl {command}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip()

    def get_clients(self) -> List[Dict[str, Any]]:
        output = self.run("-j clients")
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            return []
            
    def dispatch(self, cmd: str) -> str:
        return self.run(f"dispatch {cmd}")
        
    def keyword(self, cmd: str) -> str:
        return self.run(f"keyword {cmd}")

    def batch(self, cmds: List[str]) -> str | None:
        """
        Run multiple commands in a single hyprctl call using --batch.
        cmds: List of command strings (e.g. ["keyword windowrule ...", "dispatch move ..."])
        """
        if not cmds:
            return None
        # Join with ; and wrap in quotes. 
        # Note: simplistic joining, assumes cmds don't contain semicolons themselves that break logic
        joined = ";".join(cmds)
        return self.run(f"--batch \"{joined}\"")
