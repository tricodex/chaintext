#!/usr/bin/env python3
"""
Simple test for Gemini API
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    # Check for API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not set in .env")
        return
        
    print(f"API key found: {api_key[:5]}...{api_key[-5:]}")
    
    # Import Gemini
    try:
        from google import genai
        print("Successfully imported google.genai")
        
        # Setup client
        client = genai.Client(api_key=api_key)
        print("Created Gemini client")
        
        # Generate content
        print("\nGenerating content...")
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=["Explain Flare blockchain in one sentence"]
        )
        print(f"Response: {response.text}")
        
        # Generate embeddings
        print("\nGenerating embeddings...")
        result = client.models.embed_content(
            model="models/embedding-001",
            contents="Flare blockchain FTSO",
            task_type="retrieval_query"
        )
        
        if hasattr(result, "embeddings") and result.embeddings:
            embedding_size = len(result.embeddings)
            print(f"Generated {embedding_size} embeddings")
        else:
            print("Embedding generation returned unexpected structure")
            print(f"Result: {dir(result)}")
            
    except ImportError as ie:
        print(f"Import error: {ie}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
