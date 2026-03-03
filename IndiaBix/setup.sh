#!/usr/bin/env bash
# ==================================================
# IndiaBix Scraper - First-time Setup Script
# ==================================================
# Usage: bash setup.sh
# Run this ONCE from inside the IndiaBix/ directory.
# After setup, activate the venv and run the scraper:
#   source venv/bin/activate
#   python main.py

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "======================================"
echo " IndiaBix Scraper - Setup"
echo "======================================"

# Check Python 3 is available
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 is not installed. Please install Python 3.9+."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1)
echo "Using: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment (venv/)..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate venv
source venv/bin/activate

# Upgrade pip silently
echo ""
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install requirements
echo ""
echo "Installing requirements..."
pip install -r requirements.txt

# Create output directory
mkdir -p output

echo ""
echo "======================================"
echo " ✓ Setup complete!"
echo "======================================"
echo ""
echo "To run the IndiaBix scraper:"
echo "  cd IndiaBix"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
