#!/usr/bin/env python3
"""
Updated test script for verifying Gemini 2.0 integration
Using official syntax from the documentation
"""
import asyncio
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_gemini():
    """Test the Gemini 2.0 integration"""
    print("\n=== Testing Gemini 2.0 Integration ===\n")
    
    # Check if API key is set
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("Error: GEMINI_API_KEY is not set in .env file")
        return
    
    # Import directly to avoid any issues
    try:
        from google import genai
        client = genai.Client(api_key=gemini_api_key)
    except ImportError:
        print("Error: google-generativeai package is not installed")
        print("Install it with: pip install google-generativeai")
        return
    except Exception as e:
        print(f"Error initializing Gemini client: {e}")
        return
    
    print("1. Testing basic content generation...")
    try:
        # Use the simple syntax from the docs
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=["Explain the Flare blockchain in one paragraph"]
        )
        
        print("✅ Content generation successful:")
        print(f"Response: {response.text[:200]}...\n")
    except Exception as e:
        print(f"❌ Error testing content generation: {e}")
    
    print("2. Testing content generation with system instruction...")
    try:
        # Try using system instruction (with fallback if needed)
        sys_instruction = "You are a blockchain expert focusing on technical details."
        
        # Using direct system_instruction parameter
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                system_instruction=sys_instruction,
                contents=["What is FTSO in Flare blockchain?"]
            )
            
            print("✅ Content generation with system instruction successful:")
            print(f"Response: {response.text[:200]}...\n")
        except Exception as e:
            print(f"⚠️ System instruction parameter not supported: {e}")
            print("   Using fallback approach with system instruction in prompt...")
            
            # Fallback to including system instruction in the prompt
            enhanced_prompt = f"System instruction: {sys_instruction}\n\nUser query: What is FTSO in Flare blockchain?"
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[enhanced_prompt]
            )
            
            print("✅ Fallback system instruction successful:")
            print(f"Response: {response.text[:200]}...\n")
    except Exception as e:
        print(f"❌ Error testing content generation with system instruction: {e}")
    
    print("3. Testing structured output...")
    try:
        # Create prompt with schema as text
        schema = {
            "answer": "string",
            "confidence": "number"
        }
        
        schema_prompt = f"""What is FTSO in Flare blockchain?

Use this JSON schema:
{json.dumps(schema, indent=2)}
Return a valid JSON that follows this schema."""
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[schema_prompt]
        )
        
        print("✅ Structured output generation successful:")
        text = response.text
        print(f"Raw response: {text[:200]}...\n")
        
        # Try to extract JSON
        try:
            if "```json" in text:
                json_text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                json_text = text.split("```")[1].strip()
            else:
                # Look for JSON by braces
                start_idx = text.find('{')
                end_idx = text.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_text = text[start_idx:end_idx]
                else:
                    json_text = text
            
            parsed_json = json.loads(json_text)
            print(f"Parsed JSON: {parsed_json}\n")
        except Exception as je:
            print(f"Could not parse JSON: {je}")
    except Exception as e:
        print(f"❌ Error testing structured output: {e}")
    
    print("4. Testing embedding generation...")
    try:
        # Use the exact embedding syntax from the documentation
        result = client.models.embed_content(
            model="text-embedding-004",
            contents="Flare blockchain FTSO price feeds"
        )
        
        # Access embedding values properly
        if hasattr(result, "embeddings") and result.embeddings:
            embedding_obj = result.embeddings[0]
            if hasattr(embedding_obj, "values"):
                embedding_values = embedding_obj.values
                print(f"✅ Embedding generation successful:")
                print(f"Embedding dimensions: {len(embedding_values)}")
                print(f"Sample values: {embedding_values[:5]}...\n")
            else:
                print("❌ Embedding object does not have 'values' attribute")
        else:
            print("❌ Result object does not have 'embeddings' attribute")
    except Exception as e:
        print(f"❌ Error testing embedding generation: {e}")
    
    print("=== Gemini 2.0 Integration Test Complete ===")
    
    # Now test our wrapper from the app
    print("\n=== Testing ChainContext Wrapper ===\n")
    from app.core.genai import gemini_client
    
    print("1. Testing wrapper content generation...")
    result = await gemini_client.generate_content("What is the FTSO in Flare blockchain?")
    if result["success"]:
        print("✅ Wrapper content generation successful:")
        print(f"Response: {result['text'][:200]}...\n")
    else:
        print(f"❌ Wrapper content generation failed: {result.get('text')}")
    
    print("2. Testing wrapper structured content...")
    schema = {
        "answer": "string",
        "confidence": "number"
    }
    result = await gemini_client.generate_structured_content("What is the State Connector in Flare?", schema)
    if result["success"]:
        print("✅ Wrapper structured content generation successful:")
        print(f"Data: {result['data']}\n")
    else:
        print(f"❌ Wrapper structured content failed: {result.get('text')}")
    
    print("3. Testing wrapper embedding generation...")
    embedding = await gemini_client.embed_text("Flare blockchain FTSO price feeds")
    if embedding and len(embedding) > 0:
        print("✅ Wrapper embedding generation successful:")
        print(f"Embedding dimensions: {len(embedding)}")
        print(f"Sample values: {embedding[:5]}...\n")
    else:
        print("❌ Wrapper embedding generation failed")
    
    print("=== ChainContext Wrapper Test Complete ===")

if __name__ == "__main__":
    asyncio.run(test_gemini())
