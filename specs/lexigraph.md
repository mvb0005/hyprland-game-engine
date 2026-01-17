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
    -   (Optional) Support the existing Mobile Controller via Flask/WebSockets if needed, or potentially a pure TUI version where keyboard is used.

## 3. Requirements

### 3.1. Game Mode
For this iteration, we focus on a **Single Player** or **Hotseat** TUI version first, or a "Server View" that displays the board.

### 3.2. Core Components
1.  **LexigraphGame**: A Python class inheriting from/similar to `BoggleGame` but with Lexigraph rules (Territory Control).
2.  **LexigraphServer**: A Flask/SocketIO server (like `boggle/server.py`) to handle the game state and potentially serve the mobile controller.
3.  **LexigraphTUI**: A TUI implementation that connects to the server (or runs locally) and visualizes the grid.

### 3.3. TUI Visuals (Omarchy Style)
-   **Grid**: Displayed using ASCII/Unicode block characters or colored text.
-   **Colors**: Use ANSI color codes or a library like `rich` / `textual` to represent player ownership (Neon colors).
-   **Responsiveness**: The TUI should resize gracefully.

## 4. Implementation Plan
1.  **Port Game Logic**: Translate `lexigraph/src/server/game/*.ts` logic (Grid, Player, Move Validation) to Python.
2.  **Create TUI**: Build `lexigraph_tui.py` to render the grid.
3.  **Integrate with Engine**: Ensure it can be launched via `python games/lexigraph/main.py` (or similar).

## 5. Workflow Constraints
-   Do not modify the existing `lexigraph/` TypeScript code unless deleting it/replacing it entirely is the goal. (We will likely create a `lexigraph_python/` or use `lexigraph/` if we decide to replace the JS version).
-   **Decision**: We will create a new directory `lexigraph_py/` for the Python implementation to avoid confusion with the Node.js version during migration.

## 6. Testing
-   Unit tests for Python Game Logic (Grid, Scoring).
-   Integration test ensuring TUI can launch.
