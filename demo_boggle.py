import time
from engine import HyprlandEngine

def main():
    engine = HyprlandEngine(target_workspace=2)
    
    try:
        # Define the patterns used by this game
        game_patterns = ["BoggleBoard", "BoggleTimer", "BoggleLeaderboard", "BoggleJoin", "BoggleDebug"]
        
        # 1. Clean Slate: Kill any leftovers from previous runs
        engine.clean_slate(game_patterns)
        
        engine.switch_to_workspace()
        
        # Set a game-specific background (Dark Blue for Boggle)
        engine.set_background(color="#1e1e2e") 
        
        print("Starting Boggle Game Engine Demo...")

        # Batch definition
        windows = [
            {
                "command": "ghostty --title=BoggleBoard -e btop",
                "name_pattern": "BoggleBoard",
                "x": 50, "y": 50, "width": 1200, "height": 700
            },
            {
                "command": "ghostty --title=BoggleTimer -e sh -c 'while true; do clear; date +%S; sleep 1; done'",
                "name_pattern": "BoggleTimer",
                "x": 1300, "y": 50, "width": 500, "height": 300
            },
            {
                "command": "ghostty --title=BoggleLeaderboard -e sh -c 'echo LEADERBOARD; echo 1. MVB - 9000; read'",
                "name_pattern": "BoggleLeaderboard",
                "x": 1300, "y": 380, "width": 500, "height": 400
            },
            {
                "command": "ghostty --title=BoggleJoin -e sh -c 'echo SCAN TO JOIN; read'",
                "name_pattern": "BoggleJoin",
                "x": 1300, "y": 810, "width": 500, "height": 220
            },
            {
                "command": "ghostty --title=BoggleDebug -e python ~/code/games/grid_debug.py",
                "name_pattern": "BoggleDebug",
                "x": 50, "y": 800, "width": 1200, "height": 230
            }
        ]
        
        engine.spawn_batch(windows)

        print("Game Layout initialized. Press Ctrl+C to stop.")
        
        # Keep the script running to maintain the process handles
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping game...")
        engine.cleanup()
        # Double check cleanup
        engine.clean_slate(game_patterns)
    except Exception as e:
        print(f"Error: {e}")
        engine.cleanup()
        engine.clean_slate(game_patterns)

if __name__ == "__main__":
    main()
