import subprocess
import json

class Hyprctl:
    def run(self, command):
        cmd = f"hyprctl {command}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip()

    def get_clients(self):
        output = self.run("-j clients")
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            return []
            
    def dispatch(self, cmd):
        return self.run(f"dispatch {cmd}")
        
    def keyword(self, cmd):
        return self.run(f"keyword {cmd}")

    def batch(self, cmds):
        """
        Run multiple commands in a single hyprctl call using --batch.
        cmds: List of command strings (e.g. ["keyword windowrule ...", "dispatch move ..."])
        """
        if not cmds:
            return
        # Join with ; and wrap in quotes. 
        # Note: simplistic joining, assumes cmds don't contain semicolons themselves that break logic
        joined = ";".join(cmds)
        # We use subprocess directly here to avoid the extra "hyprctl" prefix logic in self.run if it gets complex,
        # but self.run expects the argument to follow "hyprctl".
        return self.run(f"--batch \"{joined}\"")
