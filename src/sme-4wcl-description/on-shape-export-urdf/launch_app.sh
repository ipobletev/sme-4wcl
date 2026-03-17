#!/bin/bash
set -e
# Change to the script's directory to ensure paths are correct
cd "$(dirname "$0")"

echo "Check if python is available..."
# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color
if command -v python &> /dev/null; then
    PYTHON_CMD="python"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo "Error: Neither 'python' nor 'python3' was found."
    exit 1
fi

echo "Setting up virtual environment (.venv)..."
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment using $PYTHON_CMD..."
    if ! $PYTHON_CMD -m venv .venv; then
        echo ""
        echo "Error: Failed to create virtual environment."
        
        if command -v apt &> /dev/null; then
            echo "It seems you are on a Debian/Ubuntu-based system and missing 'python3-venv'."
            echo "Installing missing dependency: sudo apt update && sudo apt install -y python3-venv"
            sudo apt update && sudo apt install -y python3-venv
            
            echo "Retrying virtual environment creation..."
            if ! $PYTHON_CMD -m venv .venv; then
                echo "Error: Failed again to create virtual environment after installation."
                exit 1
            fi
        else
            echo "Please ensure you have the 'venv' module installed for your Python version."
            exit 1
        fi
    fi
else
    echo "Using existing .venv directory."
fi

echo "Activating virtual environment..."
if [ -d ".venv/Scripts" ]; then
    source .venv/Scripts/activate
    VENV_PYTHON=".venv/Scripts/python"
else
    source .venv/bin/activate
    VENV_PYTHON=".venv/bin/python"
fi

echo "Installing dependencies from requirements.txt..."
# Use $VENV_PYTHON -m pip to avoid issues with broken shebangs in the 'pip' script
$VENV_PYTHON -m pip install -r requirements.txt

echo -e "${BLUE}Environment installed successfully.${NC}"

echo "Launch onshape-to-robot..."

if [ -d "my-robot" ]; then
    onshape-to-robot my-robot
else
    echo -e "${YELLOW}Please create 'my-robot' directory and add your robot configuration files to it.${NC}"
fi

echo -e "${GREEN}Process completed successfully.${NC}"
