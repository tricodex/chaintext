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
