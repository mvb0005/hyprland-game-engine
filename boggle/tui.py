import sys
import time
import requests
import os
import math

# ANSI Colors & Control
ESC = "\033"
CSI = f"{ESC}["
RESET = f"{CSI}0m"
BOLD = f"{CSI}1m"
RED = f"{CSI}31m"
GREEN = f"{CSI}32m"
YELLOW = f"{CSI}33m"
BLUE = f"{CSI}34m"
MAGENTA = f"{CSI}35m"
CYAN = f"{CSI}36m"
WHITE = f"{CSI}37m"

# TUI Primitives
HIDE_CURSOR = f"{CSI}?25l"
SHOW_CURSOR = f"{CSI}?25h"
CLEAR_SCREEN = f"{CSI}2J"
HOME = f"{CSI}H"

SERVER_URL = "http://127.0.0.1:8080"

def get_state():
    try:
        r = requests.get(f"{SERVER_URL}/state", timeout=0.1)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None

def draw_box(x, y, w, h, color=WHITE):
    # Box drawing chars
    TL, TR, BL, BR = "┌", "┐", "└", "┘"
    H, V = "─", "│"
    
    # Draw Top
    print(f"{CSI}{y};{x}H{color}{TL}{H*(w-2)}{TR}")
    # Draw Sides
    for i in range(1, h-1):
        print(f"{CSI}{y+i};{x}H{V}{' '*(w-2)}{V}")
    # Draw Bottom
    print(f"{CSI}{y+h-1};{x}H{BL}{H*(w-2)}{BR}{RESET}")

def centered_text(y, text, width, color=WHITE):
    x = max(1, (width - len(text)) // 2)
    print(f"{CSI}{y};{x}H{color}{text}")

def render_timer():
    print(HIDE_CURSOR + CLEAR_SCREEN)
    last_val = -1
    
    while True:
        state = get_state()
        if not state:
            time.sleep(0.5)
            continue
            
        remaining = state.get("time_remaining", 0)
        game_state = state.get("state", "UNKNOWN")
        
        # Don't redraw if same second (save CPU)
        if remaining == last_val and game_state == "PLAYING":
            time.sleep(0.1)
            continue
        last_val = remaining
            
        mins = remaining // 60
        secs = remaining % 60
        time_str = f"{mins:02}:{secs:02}"
        
        # Color Logic
        color = GREEN
        if remaining < 60: color = YELLOW
        if remaining < 10: color = RED
        if game_state != "PLAYING": 
            color = BLUE
            time_str = game_state[:8] # Truncate if needed
            
        # Draw
        print(HOME)
        # Assuming width ~20 chars (font size 60 makes it fill screen)
        # Just print big and centered
        print(f"\n\n{color}{BOLD}   {time_str}{RESET}")
        
        time.sleep(0.1)

def render_leaderboard():
    print(HIDE_CURSOR + CLEAR_SCREEN)
    
    while True:
        state = get_state()
        if not state:
            time.sleep(1)
            continue
            
        players = state.get("players", {})
        
        # Handle if players is a list (JSON array) instead of dict
        if isinstance(players, list):
            # If it's a list, assume it's already list of dicts or we can't sort by .items()
            # We need to adapt based on what the server sends.
            # If server sends [{name:..., score:...}, ...], then we just sort that.
            # But the code expected {name: {score:...}, ...}
            # Let's just print a warning and try to use it if it's iterable
            sorted_players = []
            # Fallback empty
        else:
            sorted_players = sorted(players.items(), key=lambda x: x[1]['score'], reverse=True)
        
        # Draw - Use Home to overwrite instead of clear
        print(HOME)
        print(f"{BOLD}{MAGENTA}   🏆 LEADERBOARD 🏆{RESET}")
        print(f"{CSI}2K") # Clear line
        print(f"{CSI}2K{YELLOW}{'RK':<4} {'NAME':<15} {'PTS':<5}{RESET}")
        print(f"{CSI}2K" + "-" * 30)
        
        # Clear remaining lines from previous frame roughly
        for _ in range(10): print(f"{CSI}2K") 
        print(f"{CSI}5;1H") # Back to start of list
        
        for i, (name, pdata) in enumerate(sorted_players):
            score = pdata['score']
            color = CYAN if i == 0 else WHITE
            print(f"{CSI}2K{color}{i+1:<4} {name:<15} {score:<5}{RESET}")
            
        time.sleep(1)

def render_board():
    print(HIDE_CURSOR + CLEAR_SCREEN)
    
    while True:
        state = get_state()
        if not state or not state.get("board"):
            time.sleep(0.5)
            continue
            
        board = state.get("board", [])
        
        # RENDER GRID
        # Assume 4x4 or similar
        rows = len(board)
        cols = len(board[0])
        
        # Dimensions
        cell_w = 6
        cell_h = 3
        
        # Offset
        start_x = 4
        start_y = 3
        
        print(HOME)
        print(f"{BOLD}{YELLOW}   LEXIGRID BOGGLE{RESET}")
        
        # Simple loops for grid lines to avoid complex logic
        # Top Border
        # A bit hacky but fast: just redraw everything cleanly
        
        for r in range(rows):
            y_pos = start_y + (r * cell_h)
            
            # Draw row contents
            row_line = ""
            for c in range(cols):
                char = board[r][c]
                # Dynamic color?
                color = WHITE
                if char == "Qu": char_disp = "Qu"
                else: char_disp = f" {char} " if len(char)==1 else char
                
                # Draw cell box slightly better
                # Using simple box chars for cells
                
                # We draw the content centered
                print(f"{CSI}{y_pos+1};{start_x + c*cell_w + 2}H{BOLD}{color}{char_disp}{RESET}")

        # Draw Grid Lines (Overlay)
        # Horizontal
        for r in range(rows + 1):
            py = start_y + (r * cell_h)
            line = "├" + ("─" * (cell_w-1) + "┼") * (cols-1) + "─" * (cell_w-1) + "┤"
            if r == 0: line = "┌" + ("─" * (cell_w-1) + "┬") * (cols-1) + "─" * (cell_w-1) + "┐"
            if r == rows: line = "└" + ("─" * (cell_w-1) + "┴") * (cols-1) + "─" * (cell_w-1) + "┘"
            print(f"{CSI}{py};{start_x}H{BLUE}{line}{RESET}")
            
        # Vertical
        for r in range(rows):
             for c in range(cols + 1):
                px = start_x + (c * cell_w)
                # middle parts
                for k in range(1, cell_h):
                    print(f"{CSI}{start_y + r*cell_h + k};{px}H{BLUE}│{RESET}")

        time.sleep(1)

def render_join():
    print(HIDE_CURSOR + CLEAR_SCREEN)
    while True:
        print(HOME)
        print(f"\n{BOLD}{GREEN}   JOIN GAME{RESET}")
        print(f"\n   {BLUE}{SERVER_URL}/controller{RESET}")
        print(f"\n   {YELLOW}Waiting for players...{RESET}")
        time.sleep(2)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tui.py [timer|leaderboard|board|join]")
        sys.exit(1)
        
    mode = sys.argv[1]
    
    try:
        if mode == "timer": render_timer()
        elif mode == "leaderboard": render_leaderboard()
        elif mode == "board": render_board()
        elif mode == "join": render_join()
        else: print("Unknown mode")
    except KeyboardInterrupt:
        sys.exit(0)
