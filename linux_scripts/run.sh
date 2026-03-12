#!/bin/bash
# Ensure the script runs in its own directory
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$APP_DIR"

# Activate the virtual environment
source venv/bin/activate

# Force X11 to prevent VTK/Wayland crashes on modern Linux distros
export QT_QPA_PLATFORM=xcb

# Launch the application
python app.py