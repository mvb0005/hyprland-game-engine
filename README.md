# Hyprland Native Game Engine

A modular Python framework for building "OS-level" games on [Hyprland](https://hyprland.org/). 
Instead of rendering pixels to a canvas, this engine orchestrates **native Wayland windows** (terminals) as game components.

## Philosophy
*   **The Desktop is the Board**: Game components (Board, Timer, Score) are individual floating windows.
*   **Unix Philosophy**: Each component is a simple process (script, TUI app) connected by the engine.
*   **Immersion**: A "Fake Background" layer hides the desktop, creating a dedicated game space.

## Features
*   **Atomic Spawning**: Uses `hyprctl dispatch exec [rules]` to spawn windows instantly.
*   **Python-based Game Logic**: 
    - Full **Boggle Board Generator** ported from Rust (Snake embedding algorithm).
    - **SVG-based Rendering** for high-performance, scalable board displays.
*   **Custom Backgrounds**: Spawns a dedicated, wallpaper-covering background layer.
*   **Robust Cleanup**: `clean_slate` functionality ensures no orphaned windows are left behind.

## Requirements
*   **Hyprland**: The compositor.
*   **Python 3**: The orchestration logic (Flask, etc).
*   **Ghostty / Chromium**: Recommended for windows.

## Project Structure
*   `specs/`: System specifications.
*   `engine/`: The core Python package.
*   `boggle/`: The Boggle game implementation.
    -   `boggle_game.py`: Main entry point (Orchestrator).
    -   `server.py`: Flask server handling state & UI.
    -   `game_state.py`: Core logic (Generator, Scoring).
*   `scripts/`: Utility scripts and development tools.
*   `tests/`: Unit and integration tests.
*   `docs/`: Documentation (DESIGN, STANDARDS, etc).

## Usage
Run the Boggle demo:
```bash
python boggle/boggle_game.py
```
1.  Connect via mobile/browser to `http://localhost:5000/controller`.
2.  Press **Start Game**.
