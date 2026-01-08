#!/bin/bash

# Panic Button Script

# 1. Kill the python orchestrator
pkill -f "python.*code/games"

# 2. Kill specific game windows if they linger (optional, based on class)
# pkill -f "chrome.*--app=.*boggle"

# 3. Optional: Clear workspace 2 using hyprctl
# Get all windows on workspace 2
ids=$(hyprctl clients -j | jq -r '.[] | select(.workspace.id == 2) | .address')

for id in $ids; do
    echo "Closing window $id..."
    hyprctl dispatch closewindow address:$id
done

# 4. Return to safe workspace
hyprctl dispatch workspace 1

echo "Game terminated."
