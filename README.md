# Hyprland Native Game Engine

A modular Python framework for building "OS-level" games on [Hyprland](https://hyprland.org/). 
Instead of rendering pixels to a canvas, this engine orchestrates **native Wayland windows** (terminals) as game components.

## Philosophy
*   **The Desktop is the Board**: Game components (Board, Timer, Score) are individual floating windows.
*   **Unix Philosophy**: Each component is a simple process (script, TUI app) connected by the engine.
*   **Immersion**: A "Fake Background" layer hides the desktop, creating a dedicated game space.

## Features
*   **Atomic Spawning**: Uses `hyprctl dispatch exec [rules]` to spawn windows instantly in their correct floating position/size, eliminating visual "tiling" glitches.
*   **Batch Processing**: Spawns dozens of windows simultaneously with minimal IPC overhead.
*   **Custom Backgrounds**: Spawns a dedicated, wallpaper-covering background layer (using `imv`) that sits behind game windows but covers the workspace.
*   **Robust Cleanup**: `clean_slate` functionality ensures no orphaned windows are left behind.

## Requirements
*   **Hyprland**: The compositor.
*   **Python 3**: The orchestration logic.
*   **Ghostty**: The terminal emulator used for game windows (fast, GPU-accelerated).
*   **IMV**: Image viewer used for the background layer.
*   **ImageMagick**: Used to generate solid color backgrounds on the fly.

## Project Structure
*   `engine/`: The core Python package.
    *   `core.py`: Low-level Hyprland IPC.
    *   `window.py`: Window lifecycle management (spawn, move, resize, close).
    *   `background.py`: Manages the background layer.
*   `demo_boggle.py`: The main proof-of-concept game layout.
*   `ghostty_game.conf`: Minimal Ghostty configuration for "game-like" terminals.

## Usage
Run the Boggle demo:
```bash
python demo_boggle.py
```
*   **Exit**: Press `Ctrl+C` in the terminal running the script.
*   **Emergency Kill**: If configured, press `Super + Escape` (triggers `kill_game.sh`).
