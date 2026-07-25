#!/usr/bin/env bash
#
# Sets up the local Python environment for the RAG retrieval engine
# (retrieval-augmented-generation/): creates a virtual environment (if one doesn't
# already exist) and installs dependencies from requirements.txt.
#
# Usage (from the repo root):
#   ./install.sh
#
# Safe to re-run — skips venv creation if it already exists, and
# reinstalling dependencies is a no-op if they're already satisfied.

set -e  # stop immediately if any step fails

# Always operate relative to this script's own location, regardless of
# which directory it's called from, then step into the Python folder.
cd "$(dirname "$0")/retrieval-augmented-generation"

echo "Checking for python3..."
if ! command -v python3 &> /dev/null; then
    echo "python3 not found. Install Python 3 first: https://www.python.org/downloads/"
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists, skipping creation."
fi

echo "Installing dependencies from requirements.txt..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

echo ""
echo "Setup complete."
echo "Before running ingest.py or retrieve.py:"
echo "  cd retrieval-augmented-generation && source venv/bin/activate"
