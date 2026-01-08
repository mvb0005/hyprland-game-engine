# Hyprland Game Engine Design
## Concept
Use the Hyprland Wayland compositor as a dynamic game UI framework. Instead of building a monolithic full-screen game application, we compose the game interface using multiple independent OS-level windows (Web Apps, Terminals, TUIs) arranged precisely on the screen.

## Architecture

### Workspaces
- **Workspace 1 (Admin/Server)**: Where the game logic server runs. Kept safe from automation.
- **Workspace 2 (Game View)**: The public-facing display where windows are orchestrated.

### The Orchestrator (Engine)
A Python-based controller that interacts with Hyprland via `hyprctl`.

**Responsibilities:**
1.  **Lifecycle Management**: Spawning and killing window processes.
2.  **Window Identification**: using specific `class` or `title` rules to grab handle of specific windows.
3.  **Layout**: Positioning and resizing windows (Board, Timer, Leaderboard).
4.  **State Management**: Dynamic resizing or moving based on game events (e.g., "Timer gets bigger when 10s remain").

### Safety / Escape Hatch
A global "Panic Button" script that:
1.  Kills the orchestrator process.
2.  Closes all windows tagged with `game-component`.
3.  Returns focus to Workspace 1.

### Example: Boggle
**Windows:**
1.  **Board**: Central web view showing the grid.
2.  **Timer**: Large text display (TUI or Web).
3.  **Leaderboard**: Side list of players/scores.
4.  **QR Code**: Small corner window for joining via mobile.
5.  **Status**: Game phase indicator (Lobby, Playing, Voting).

## Technical Implementation
- **Communication**: `hyprctl -j clients` to find window addresses. `hyprctl dispatch` to move/resize.
- **Content**: Chrome in `--app` mode for easy HTML/JS rendering.
- **Input**: Mobile phones act as controllers (server handles this), so the Hyprland windows are mostly *displays*.

## Directory Structure
- `engine.py`: Main python orchestrator class.
- `demo_boggle.py`: Specific implementation for Boggle layout.
- `kill_game.sh`: Cleanup script.
