#!/bin/bash
echo "======================================"
echo " Installing MOLD F.O.R.G.E (Linux)    "
echo "======================================"

# Ensure the script runs in its own directory
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$APP_DIR"

echo "[1/4] Checking for compatible Python version..."
# CadQuery/OCP currently support Python 3.9 up to 3.12. 
# We explicitly search for these versions to avoid bleeding-edge versions.
PYTHON_EXE=""
for version in "3.11" "3.10" "3.12" "3.9"; do
    if command -v "python$version" &> /dev/null; then
        PYTHON_EXE="python$version"
        break
    fi
done

if [ -z "$PYTHON_EXE" ]; then
    echo "ERROR: No compatible Python version found."
    echo "MOLD F.O.R.G.E. requires Python 3.9, 3.10, 3.11, or 3.12."
    echo "Your system default might be too new"
    echo "Please install python3.11 via your package manager and try again."
    exit 1
fi

echo "Found compatible Python: $PYTHON_EXE"

echo "[2/4] Creating local virtual environment (venv)..."
$PYTHON_EXE -m venv venv

echo "[3/4] Activating venv and installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "[4/4] Creating application menu icon..."
DESKTOP_DIR="$HOME/.local/share/applications"
mkdir -p "$DESKTOP_DIR"
DESKTOP_FILE="$DESKTOP_DIR/moldforge.desktop"

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
echo " You can now search for 'MOLD F.O.R.G.E.' in your system menu."
echo "======================================"