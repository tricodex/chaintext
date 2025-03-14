#!/bin/bash
# Verbose setup script for troubleshooting Gemini installation

# Exit on error
set -e

echo "Setting up test environment with verbose output..."

# Create a fresh virtual environment
echo "Creating virtual environment..."
rm -rf .venv-test2
python3 -m venv .venv-test2
source .venv-test2/bin/activate

# Show Python info
echo "Python version:"
python --version
echo "Python path:"
which python
echo "Pip path:"
which pip

# Install dependencies step by step
echo "Installing dotenv..."
pip install python-dotenv

echo "Installing google-generativeai with verbose output..."
pip install -v google-generativeai==0.5.0

echo "Checking installed packages:"
pip list

# Write a test script
cat > test_import.py << 'EOL'
#!/usr/bin/env python3
"""
Test script to check Gemini imports
"""
import sys
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path}")

print("\nTrying to import google.generativeai...")
try:
    import google.generativeai
    print("✅ Successfully imported google.generativeai")
    print(f"Module location: {google.generativeai.__file__}")
except ImportError as e:
    print(f"❌ Import error: {e}")

print("\nTrying alternative import...")
try:
    from google import genai
    print("✅ Successfully imported genai from google")
    print(f"Module location: {genai.__file__ if hasattr(genai, '__file__') else 'Unknown'}")
except ImportError as e:
    print(f"❌ Import error: {e}")

print("\nChecking google package structure...")
try:
    import google
    print(f"Google package location: {google.__file__}")
    print(f"Google package contents: {dir(google)}")
except ImportError as e:
    print(f"❌ Cannot import google: {e}")
EOL

# Run the test
echo "Running import test..."
python test_import.py

# Deactivate venv
deactivate

echo "Test complete!"
