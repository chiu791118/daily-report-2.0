#!/bin/bash
# Installation script for Daily Market Digest
# Run this script to set up the Python environment and install dependencies

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "========================================"
echo "Daily Market Digest - Installation"
echo "========================================"
echo ""
echo "Project directory: $PROJECT_DIR"
echo ""

cd "$PROJECT_DIR"

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Python version: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies with retry
echo ""
echo "Installing dependencies..."
echo "This may take a while depending on your network connection."
echo ""

# Function to install with retry
install_package() {
    local package=$1
    local max_retries=3
    local retry=0

    while [ $retry -lt $max_retries ]; do
        echo "Installing $package (attempt $((retry+1))/$max_retries)..."
        if pip install --default-timeout=120 "$package" 2>/dev/null; then
            echo "✅ $package installed successfully"
            return 0
        fi
        retry=$((retry+1))
        if [ $retry -lt $max_retries ]; then
            echo "Retrying in 5 seconds..."
            sleep 5
        fi
    done

    echo "❌ Failed to install $package after $max_retries attempts"
    return 1
}

# Install packages in order
echo "Installing core packages..."
install_package "python-dotenv"
install_package "pyyaml"
install_package "pytz"
install_package "python-dateutil"

echo ""
echo "Installing news collection packages..."
install_package "feedparser"
install_package "requests"

echo ""
echo "Installing data analysis packages..."
install_package "pandas"
install_package "numpy"
install_package "yfinance"

echo ""
echo "Installing Google packages..."
install_package "google-api-python-client"
install_package "youtube-transcript-api"
install_package "google-generativeai"

echo ""
echo "Installing Notion client..."
install_package "notion-client"

# Check installation
echo ""
echo "========================================"
echo "Verifying installation..."
echo "========================================"

python3 -c "
import sys
packages = [
    'dotenv',
    'yaml',
    'pytz',
    'dateutil',
    'feedparser',
    'requests',
    'pandas',
    'numpy',
    'yfinance',
    'googleapiclient',
    'youtube_transcript_api',
    'google.generativeai',
    'notion_client',
]

failed = []
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✅ {pkg}')
    except ImportError as e:
        failed.append(pkg)
        print(f'❌ {pkg}: {e}')

if failed:
    print(f'\\n⚠️  Failed to import: {failed}')
    sys.exit(1)
else:
    print('\\n✅ All packages installed successfully!')
"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys"
fi

echo ""
echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API keys"
echo "2. Test the installation:"
echo "   cd $PROJECT_DIR"
echo "   source .venv/bin/activate"
echo "   python src/main.py test"
echo ""
