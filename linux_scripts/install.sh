#!/bin/bash
echo "======================================"
echo " Installing MOLD F.O.R.G.E (Linux)    "
echo "======================================"

# Ensure the script runs in its own directory
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$APP_DIR"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 could not be found. Please install it via your package manager."
    exit 1
fi

echo "[1/4] Creating local virtual environment (venv)..."
python3 -m venv venv

echo "[2/4] Activating venv and upgrading pip..."
source venv/bin/activate
pip install --upgrade pip

echo "[3/4] Installing dependencies (this may take a few minutes)..."
pip install -r requirements.txt

echo "[4/4] Creating application menu icon..."
# Standard Linux directory for user-specific desktop entries
DESKTOP_DIR="$HOME/.local/share/applications"
mkdir -p "$DESKTOP_DIR"
DESKTOP_FILE="$DESKTOP_DIR/moldforge.desktop"

# Create the .desktop file
cat <<EOF > "$DESKTOP_FILE"
[Desktop Entry]
Version=1.0
Name=MOLD F.O.R.G.E.
Comment=Fingerboard Design Suite
Exec="$APP_DIR/run.sh"
Icon=$APP_DIR/icon.ico
Terminal=false
Type=Application
Categories=Graphics;3DGraphics;Engineering;
EOF

chmod +x "$DESKTOP_FILE"

echo "======================================"
echo " INSTALLATION COMPLETED SUCCESSFULLY! "
echo " You can now search for 'MOLD F.O.R.G.E.' in your system menu"
echo " and pin it to your taskbar/dock."
echo "======================================"