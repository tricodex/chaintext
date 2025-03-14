#!/usr/bin/env python3
"""
Test script for verifying Gemini integration
"""
import asyncio
import os
from dotenv import load_dotenv
from app.core.genai import gemini_client

# Load environment variables
load_dotenv()

async def test_gemini():
    """Test the Gemini integration"""
    print("\n=== Testing Gemini Integration ===\n")
    
    # Check if API key is set
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY is not set in .env file")
        return
    
    # Check if client is available
    if not gemini_client.available:
        print("Error: Gemini client is not available")
        return
    
    print("1. Testing content generation...")
    try:
        result = await gemini_client.generate_content("Explain the Flare blockchain in one paragraph")
        if result["success"]:
            print("✅ Content generation successful:")
            print(f"Response: {result['text'][:150]}...\n")
        else:
            print(f"❌ Content generation failed: {result.get('text')}")
    except Exception as e:
        print(f"❌ Error testing content generation: {e}")
    
    print("2. Testing structured content generation...")
    try:
        schema = {
            "answer": "string",
            "confidence": "number"
        }
        result = await gemini_client.generate_structured_content(
            "What is FTSO in Flare blockchain?", 
            schema
        )
        if result["success"]:
            print("✅ Structured content generation successful:")
            print(f"Data: {result['data']}\n")
        else:
            print(f"❌ Structured content generation failed: {result.get('text')}")
    except Exception as e:
        print(f"❌ Error testing structured content generation: {e}")
    
    print("3. Testing embedding generation...")
    try:
        embedding = await gemini_client.embed_text("Flare blockchain FTSO price feeds")
        if embedding and len(embedding) > 0:
            print(f"✅ Embedding generation successful: {len(embedding)} dimensions")
            print(f"Sample: {embedding[:5]}...\n")
        else:
            print("❌ Embedding generation failed or returned empty embedding")
    except Exception as e:
        print(f"❌ Error testing embedding generation: {e}")
    
    print("=== Gemini Integration Test Complete ===")

if __name__ == "__main__":
    asyncio.run(test_gemini())
