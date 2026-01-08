from typing import List, Dict, Any, Optional
from .core import Hyprctl
from .window import WindowManager
from .background import BackgroundManager

class HyprlandEngine:
    def __init__(self, target_workspace: int = 2):
        self.hyprctl = Hyprctl()
        self.wm = WindowManager(self.hyprctl, target_workspace)
        self.bg = BackgroundManager(self.hyprctl, target_workspace)
        self.workspace = target_workspace

    def switch_to_workspace(self) -> None:
        print(f"Switching to workspace {self.workspace}...")
        self.hyprctl.dispatch(f"workspace {self.workspace}")

    def spawn_batch(self, windows_config: List[Dict[str, Any]]) -> None:
        return self.wm.spawn_batch(windows_config)

    def spawn_window(self, command: str, title_pattern: str, x: int, y: int, width: int, height: int, app_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        # Determine if we should treat title_pattern as a class or title
        # For this engine, let's assume if the command contains --class, we use class matching
        # But to be safe and compatible with previous demo, we check if app_id is passed or just use title_pattern
        
        use_class = False
        if "--class" in command:
            use_class = True
            
        return self.wm.spawn(command, title_pattern, x, y, width, height, is_class=use_class)

    def set_background(self, *args: Any, **kwargs: Any) -> None:
        return self.bg.set(*args, **kwargs)

    def cleanup(self) -> None:
        print("Engine shutting down...")
        self.bg.cleanup()
        self.wm.cleanup()

    def clean_slate(self, patterns: List[str]) -> None:
        """
        Aggressively close any window matching the patterns to ensure a clean slate.
        """
        self.wm.close_matching(patterns)
        self.bg.cleanup() # Also kill old backgrounds
