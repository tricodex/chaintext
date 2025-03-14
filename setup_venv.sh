#!/bin/bash
# Setup script for ChainContext backend
# This script creates a virtual environment using uv and installs requirements

# Exit on error
set -e

echo "Setting up ChainContext backend..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Create .venv directory if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
source .venv/bin/activate

# Install uv package manager
echo "Installing uv package manager..."
pip install uv

# Install dependencies using uv
echo "Installing dependencies with uv..."
uv pip install -r requirements.txt

# Check if Google Generative AI is installed
if ! uv pip show google-generativeai &> /dev/null; then
    echo "Installing google-generativeai package..."
    uv pip install google-generativeai
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "Please edit .env file to set your GEMINI_API_KEY."
fi

echo "Setup complete! You can now run the application with:"
echo "source .venv/bin/activate"
echo "python dev.py"
