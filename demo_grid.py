import time
from engine import HyprlandEngine

def main():
    engine = HyprlandEngine(target_workspace=2)
    
    try:
        engine.switch_to_workspace()
        
        # Solid background to verify gaps
        engine.set_background(color="#222222") 
        
        print("Starting 5x5 Grid Demo...")

        # Grid Configuration
        rows = 5
        cols = 5
        screen_w = 1920
        screen_h = 1080
        
        # Margins
        margin_x = 100
        margin_y = 100
        gap = 10
        
        # Calculate cell size
        avail_w = screen_w - (2 * margin_x) - ((cols - 1) * gap)
        avail_h = screen_h - (2 * margin_y) - ((rows - 1) * gap)
        
        cell_w = int(avail_w / cols)
        cell_h = int(avail_h / rows)
        
        windows = []
        
        for r in range(rows):
            for c in range(cols):
                idx = (r * cols) + c + 1
                
                # Calculate Pos
                x = margin_x + (c * (cell_w + gap))
                y = margin_y + (r * (cell_h + gap))
                
                name = f"GridWin_{idx}"
                cmd = f"ghostty --title={name} --config-file=~/code/games/ghostty_game.conf -e sh -c 'echo {idx}; sleep infinity'"
                
                windows.append({
                    "command": cmd,
                    "name_pattern": name,
                    "x": x,
                    "y": y,
                    "width": cell_w,
                    "height": cell_h
                })

        print(f"Generated {len(windows)} window configurations.")
        print(f"Cell Size: {cell_w}x{cell_h}")
        
        engine.spawn_batch(windows)

        print("Grid initialized. Press Ctrl+C to stop.")
        
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping grid demo...")
        engine.cleanup()
    except Exception as e:
        print(f"Error: {e}")
        engine.cleanup()

if __name__ == "__main__":
    main()
