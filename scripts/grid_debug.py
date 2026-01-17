import curses
from engine import HyprlandEngine

def draw_grid(stdscr):
    # Setup curses
    curses.curs_set(0)
    stdscr.clear()
    
    engine = HyprlandEngine(target_workspace=2)
    
    while True:
        try:
            stdscr.clear()
            clients = engine.hyprctl.get_clients()
            
            # Filter for our workspace
            workspace_clients = [c for c in clients if c['workspace']['id'] == 2]
            
            stdscr.addstr(0, 0, f"Hyprland Grid Debugger (Workspace 2) - {len(workspace_clients)} windows")
            
            row = 2
            stdscr.addstr(row, 0, f"{'Title':<25} {'Addr':<10} {'X':<5} {'Y':<5} {'W':<5} {'H':<5} {'Class'}")
            row += 1
            stdscr.addstr(row, 0, "-"*80)
            row += 1
            
            for c in workspace_clients:
                title = c['title'][:23]
                addr = c['address']
                x = c['at'][0]
                y = c['at'][1]
                w = c['size'][0]
                h = c['size'][1]
                cls = c['class'][:15]
                
                try:
                    stdscr.addstr(row, 0, f"{title:<25} {addr:<10} {x:<5} {y:<5} {w:<5} {h:<5} {cls}")
                except curses.error:
                    pass # Window too small
                row += 1
                
            stdscr.refresh()
            stdscr.timeout(500) # Refresh every 0.5s
            c = stdscr.getch()
            if c == ord('q'):
                break
        except Exception:
            pass

if __name__ == "__main__":
    curses.wrapper(draw_grid)
