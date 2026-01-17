#!/bin/bash
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Run ./setup_dev.sh first."
    exit 1
fi

source .venv/bin/activate
TARGET=${1:-demo_boggle.py}

echo "Watching for changes to restart: $TARGET"
watchfiles "python $TARGET" .
