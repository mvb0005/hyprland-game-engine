# Hyprland Game Engine Project

## Completed Tasks
- [x] **Core Engine**
    - [x] `engine.core`: Basic Hyprland IPC wrapper (sockets/JSON).
    - [x] `engine.window`: Advanced window management with atomic spawning (no visual glitches).
    - [x] `engine.background`: Robust background layer using IMV (supports solid colors & images).
    - [x] Batch processing for high-performance layout initialization.
- [x] **Demos**
    - [x] `demo_boggle.py`: A full layout test with Board, Timer, Leaderboard, and Join instructions.
    - [x] `demo_grid.py`: 5x5 Grid layout stress test.
- [x] **Utilities**
    - [x] `ghostty_game.conf`: Minimal terminal config (no cursor, no decorations).
    - [x] `kill_game.sh`: Emergency kill switch (`Super + Escape`).
    - [x] `grid_debug.py`: TUI for inspecting window geometries.

## Roadmap
- [ ] **Game Logic Implementation**
    - [ ] **Boggle**:
        - [ ] Connect `BoggleBoard` to a backend game state.
        - [ ] Implement interactive Timer.
        - [ ] Real-time Leaderboard updates.
    - [ ] **New Games**:
        - [ ] Memory Match (Grid based).
        - [ ] Battleship.
- [ ] **System Features**
    - [ ] **Game Launcher**: A "Start Menu" window to select games.
    - [ ] **Input Handling**: Centralized input controller (sockets?) to route keystrokes to specific windows.
    - [ ] **Dynamic Resizing**: Handle monitor resolution changes gracefully.
    - [ ] **Sound**: Add sound effects for game events.
