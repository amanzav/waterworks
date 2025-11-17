#!/bin/bash
# Waterworks - One-Line Installer for macOS/Linux
# Usage: curl -sSL https://raw.githubusercontent.com/amanzav/waterworks/main/install.sh | bash

set -e

echo "💧 Waterworks - Easy Installer"
echo "=============================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed."
    echo ""
    echo "Please install Python 3.9 or higher:"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "  brew install python3"
    else
        echo "  sudo apt-get install python3 python3-venv python3-pip"
    fi
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.9"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $PYTHON_VERSION found, but Python 3.9+ is required"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION found"
echo ""

# Set installation directory
INSTALL_DIR="$HOME/waterworks"

# Ask user for installation directory
read -p "Install to [$INSTALL_DIR]: " USER_DIR
if [ ! -z "$USER_DIR" ]; then
    INSTALL_DIR="$USER_DIR"
fi

echo ""
echo "📦 Installing to: $INSTALL_DIR"
echo ""

# Create directory
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Download only essential files (not the entire repo)
echo "⬇️  Downloading Waterworks files..."

BASE_URL="https://raw.githubusercontent.com/amanzav/waterworks/main"

# Download main files
curl -sSL "$BASE_URL/requirements.txt" -o requirements.txt
curl -sSL "$BASE_URL/main.py" -o main.py
curl -sSL "$BASE_URL/setup.py" -o setup.py

# Download modules
mkdir -p modules
curl -sSL "$BASE_URL/modules/__init__.py" -o modules/__init__.py
curl -sSL "$BASE_URL/modules/auth.py" -o modules/auth.py
curl -sSL "$BASE_URL/modules/config_manager.py" -o modules/config_manager.py
curl -sSL "$BASE_URL/modules/cover_letter_generator.py" -o modules/cover_letter_generator.py
curl -sSL "$BASE_URL/modules/folder_navigator.py" -o modules/folder_navigator.py
curl -sSL "$BASE_URL/modules/job_extractor.py" -o modules/job_extractor.py
curl -sSL "$BASE_URL/modules/pdf_builder.py" -o modules/pdf_builder.py
curl -sSL "$BASE_URL/modules/utils.py" -o modules/utils.py

echo "✅ Files downloaded"
echo ""

# Create virtual environment
echo "🔧 Setting up virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo "✅ Dependencies installed"
echo ""

# Check for platform-specific tools
if [[ "$OSTYPE" == "darwin"* ]]; then
    if ! command -v libreoffice &> /dev/null && ! command -v soffice &> /dev/null; then
        echo "⚠️  LibreOffice not found (needed for PDF conversion)"
        echo "   Install with: brew install libreoffice"
        echo ""
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if ! command -v libreoffice &> /dev/null && ! command -v soffice &> /dev/null; then
        echo "⚠️  LibreOffice not found (needed for PDF conversion)"
        echo "   Install with: sudo apt-get install libreoffice"
        echo ""
    fi
fi

# Create launcher script
cat > waterworks << 'EOF'
#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPT_DIR/venv/bin/activate"
python "$SCRIPT_DIR/main.py" "$@"
EOF

chmod +x waterworks

# Create alias in shell config
SHELL_CONFIG=""
if [ -f "$HOME/.zshrc" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
elif [ -f "$HOME/.bash_profile" ]; then
    SHELL_CONFIG="$HOME/.bash_profile"
fi

if [ ! -z "$SHELL_CONFIG" ]; then
    if ! grep -q "alias waterworks=" "$SHELL_CONFIG"; then
        echo "" >> "$SHELL_CONFIG"
        echo "# Waterworks alias" >> "$SHELL_CONFIG"
        echo "alias waterworks='$INSTALL_DIR/waterworks'" >> "$SHELL_CONFIG"
        echo "✅ Added 'waterworks' command to $SHELL_CONFIG"
        echo "   Run: source $SHELL_CONFIG  (or restart terminal)"
    fi
fi

echo ""
echo "=============================="
echo "✅ Installation Complete!"
echo "=============================="
echo ""
echo "Next steps:"
echo "  1. Restart your terminal (or run: source $SHELL_CONFIG)"
echo "  2. Run: waterworks config --show  (or: $INSTALL_DIR/waterworks config --show)"
echo ""
echo "If config not found:"
echo "  1. Run setup: cd $INSTALL_DIR && source venv/bin/activate && python setup.py"
echo "  2. Then: waterworks generate --folder <folder_name>"
echo ""
echo "Documentation: https://github.com/amanzav/waterworks"
echo ""
