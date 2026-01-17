
import hyprpy
import inspect

# print("hyprpy version:", hyprpy.__version__)
print("\nClasses/Functions in hyprpy:")
for name, obj in inspect.getmembers(hyprpy):
    if not name.startswith("_"):
        print(f"- {name}")

try:
    from hyprpy import Hyprland
    print("\nHyprland class found. Attempting connection...")
    instance = Hyprland()
    print("\nCommand Socket type:")
    print(type(instance.command_socket))
    print([d for d in dir(instance.command_socket) if not d.startswith('_')])
    
    print("\nTesting connection by fetching windows...")
    windows = instance.get_windows()
    print(f"Found {len(windows)} windows.")
    if windows:
        w = windows[0]
        print(f"  Sample Window: {w.title} (Class: {w.wm_class})")
        print("  Attributes:", [d for d in dir(w) if not d.startswith('_')])
        
except Exception as e:
    print(f"\nError using hyprpy: {e}")
