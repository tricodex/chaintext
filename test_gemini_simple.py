#!/usr/bin/env python3
"""
Simple test script for the updated Gemini integration
"""
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_gemini():
    """Test Gemini integration using our client implementation"""
    print("\n=== Testing Gemini Integration ===\n")
    
    # Import our client implementation
    from app.core.genai import gemini_client
    
    # Check if client is available
    if not gemini_client.available:
        print("❌ Gemini client is not available. Check your API key and installation.")
        return
    
    print("✅ Gemini client is available")
    
    # Test simple content generation
    print("\n1. Testing simple content generation...")
    result = await gemini_client.generate_content("What is the Flare blockchain?")
    
    if result["success"]:
        print("✅ Content generation successful")
        print(f"Response: {result['text'][:200]}...")
    else:
        print(f"❌ Content generation failed: {result.get('text')}")
    
    # Test structured content generation
    print("\n2. Testing structured content generation...")
    schema = {
        "answer": "string",
        "confidence": "number"
    }
    
    result = await gemini_client.generate_structured_content(
        "What is FTSO in Flare blockchain?", 
        schema
    )
    
    if result["success"]:
        print("✅ Structured content generation successful")
        if result.get("data"):
            print(f"Structured data: {result['data']}")
        else:
            print(f"Raw response: {result['text'][:200]}...")
    else:
        print(f"❌ Structured content generation failed: {result.get('text')}")
    
    # Test embedding generation
    print("\n3. Testing embedding generation...")
    embedding = await gemini_client.embed_text("Flare blockchain FTSO price feeds")
    
    if embedding and len(embedding) > 0:
        print(f"✅ Embedding generation successful: {len(embedding)} dimensions")
        print(f"Sample values: {embedding[:5]}...")
    else:
        print("❌ Embedding generation failed")
    
    print("\n=== Gemini Integration Test Complete ===")

if __name__ == "__main__":
    asyncio.run(test_gemini())
