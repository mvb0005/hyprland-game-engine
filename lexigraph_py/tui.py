import time
import sys
import os
import threading
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.align import Align

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexigraph_py.game import LexigraphGame
from lexigraph_py.server import run_server, game as server_game

class LexigraphTUI:
    def __init__(self):
        self.console = Console()
        self.game = server_game # Use the shared game instance from server module
        self.layout = Layout()
        
    def generate_grid_table(self):
        table = Table(show_header=False, show_edge=False, padding=0, expand=True)
        
        # Add columns
        for _ in range(self.game.grid.width):
            table.add_column(justify="center")
            
        for y in range(self.game.grid.height):
            cells = []
            for x in range(self.game.grid.width):
                tile = self.game.grid.get_tile(x, y)
                color = "white"
                bg_color = "black"
                
                if tile.owner:
                    # Convert hex to generic color name or leave as hex if rich supports it (it does usually)
                    # Mapping generic hexes to rich colors for better compatibility if needed
                    # but rich handles hex like #FF0055 directly.
                    color = "black" # Text color on colored tile
                    bg_color = tile.owner.color
                
                cell_content = f"[{color} on {bg_color}] {tile.char} [/{color} on {bg_color}]"
                # Make it look like a block
                cell_block = f"[{color} on {bg_color}]   \n {tile.char} \n   [/{color} on {bg_color}]"
                cells.append(cell_block)
            table.add_row(*cells)
            # Add spacer row?
            
        return Panel(Align.center(table), title="Lexigraph Grid", border_style="green")

    def generate_leaderboard(self):
        table = Table(title="Leaderboard", expand=True)
        table.add_column("Rank", justify="right", style="cyan", no_wrap=True)
        table.add_column("Player", style="magenta")
        table.add_column("Score", justify="right", style="green")

        sorted_players = sorted(self.game.players.values(), key=lambda p: p.score, reverse=True)
        
        for i, player in enumerate(sorted_players):
            table.add_row(str(i+1), f"[{player.color}]{player.name}[/]", str(player.score))
            
        return Panel(table, title="Scores", border_style="blue")

    def make_layout(self):
        self.layout.split_row(
            Layout(name="grid", ratio=2),
            Layout(name="sidebar", ratio=1)
        )
        self.layout["grid"].update(self.generate_grid_table())
        self.layout["sidebar"].update(self.generate_leaderboard())
        return self.layout

    def run(self):
        # Start server in a separate thread
        server_thread = threading.Thread(target=run_server, kwargs={'port': 3000}, daemon=True)
        server_thread.start()
        
        self.console.clear()
        
        with Live(self.make_layout(), refresh_per_second=4, screen=True) as live:
            while True:
                live.update(self.make_layout())
                time.sleep(0.25)

if __name__ == "__main__":
    tui = LexigraphTUI()
    try:
        tui.run()
    except KeyboardInterrupt:
        print("Exiting...")
