# Lexigraph TUI Specification

## 1. Overview
This specification describes the **TUI (Text User Interface)** implementation of the Lexigraph game, replacing the existing web-based TV view.

## 2. Architecture
The game will run within the Hyprland Game Engine environment.

-   **Game Logic**: Python (reusing/porting logic from `boggle/` or adapting `lexigraph/` logic).
-   **Display**: A native terminal window running a TUI application (likely `textual` or `curses` or custom TUI).
-   **Integration**:
    -   Run as a "Game" within the `engine` framework.
    -   Use `engine` to spawn the window.
    -   **Mobile Controller**: The game MUST support the existing web-based mobile controller. The Python server will serve the static files for the controller and handle WebSocket events from it.

## 3. Requirements

### 3.1. Game Mode
For this iteration, we focus on a **Hybrid Mode**:
-   **TV/Server View**: A TUI window running on the host (Hyprland).
-   **Controller**: Players use their phones (web browser) to input moves.

### 3.2. Core Components
1.  **LexigraphGame**: A Python class inheriting from/similar to `BoggleGame` but with Lexigraph rules (Territory Control).
2.  **LexigraphServer**: A Flask/SocketIO server (like `boggle/server.py`) to handle the game state and serve the mobile controller files.
3.  **LexigraphTUI**: A TUI implementation that renders the grid state.

### 3.3. TUI Visuals (Omarchy Style)
-   **Grid**: Displayed using ASCII/Unicode block characters or colored text.
-   **Colors**: Use ANSI color codes or a library like `rich` / `textual` to represent player ownership (Neon colors).
-   **Responsiveness**: The TUI should resize gracefully.
-   **Updates**: The TUI must update in real-time as players make moves on their phones.

## 4. Implementation Plan
1.  **Port Game Logic**: Translate `lexigraph/src/server/game/*.ts` logic (Grid, Player, Move Validation) to Python.
2.  **Migrate Controller**: Copy/move the frontend controller code from `lexigraph/src/controller` to a location servable by the Python app (e.g., `lexigraph_py/static/controller`).
3.  **Create Server**: Implement `lexigraph_py/server.py` using Flask-SocketIO to serve the controller and handle events.
4.  **Create TUI**: Build `lexigraph_py/tui.py` to render the grid, consuming state from the server/game instance.
5.  **Integrate with Engine**: Ensure it can be launched via `python games/lexigraph/main.py` (or similar).

## 5. Workflow Constraints
-   **Legacy Code**: The existing `lexigraph/` folder contains the TypeScript implementation. We will treat `lexigraph/src/controller` as the source of truth for the frontend code, but migrate the backend logic to Python.
-   **Decision**: We will create a new directory `lexigraph_py/` for the Python implementation.

## 6. Testing
-   Unit tests for Python Game Logic (Grid, Scoring).
-   Integration test ensuring TUI can launch.
-   Verification that the mobile controller can connect to the Python server.
