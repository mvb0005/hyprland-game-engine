from .core import Hyprctl
from .window import WindowManager
from .background import BackgroundManager

class HyprlandEngine:
    def __init__(self, target_workspace=2):
        self.hyprctl = Hyprctl()
        self.wm = WindowManager(self.hyprctl, target_workspace)
        self.bg = BackgroundManager(self.hyprctl, target_workspace)
        self.workspace = target_workspace

    def switch_to_workspace(self):
        print(f"Switching to workspace {self.workspace}...")
        self.hyprctl.dispatch(f"workspace {self.workspace}")

    def spawn_batch(self, windows_config):
        return self.wm.spawn_batch(windows_config)

    def spawn_window(self, command, title_pattern, x, y, width, height, app_id=None):
        # Determine if we should treat title_pattern as a class or title
        # For this engine, let's assume if the command contains --class, we use class matching
        # But to be safe and compatible with previous demo, we check if app_id is passed or just use title_pattern
        
        use_class = False
        if "--class" in command:
            use_class = True
            
        return self.wm.spawn(command, title_pattern, x, y, width, height, is_class=use_class)

    def set_background(self, *args, **kwargs):
        return self.bg.set(*args, **kwargs)

    def cleanup(self):
        print("Engine shutting down...")
        self.bg.cleanup()
        self.wm.cleanup()

    def clean_slate(self, patterns):
        """
        Aggressively close any window matching the patterns to ensure a clean slate.
        """
        self.wm.close_matching(patterns)
        self.bg.cleanup() # Also kill old backgrounds
