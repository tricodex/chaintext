#!/usr/bin/env python3
"""
Simple test script that directly uses the Google Generative AI package
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_simple_gemini():
    """Test simple Gemini API calls"""
    print("\n=== Simple Gemini Test ===\n")
    
    # Check if API key is set
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("Error: GEMINI_API_KEY is not set in .env file")
        return
    
    # Import directly
    try:
        from google import genai
        
        # Initialize the client
        genai.configure(api_key=gemini_api_key)
        
        # Test basic content generation
        print("Testing content generation...")
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("What is the FTSO in Flare blockchain?")
        
        print("Content generation successful:")
        print(f"Response: {response.text[:200]}...\n")
        
        # Test embedding generation
        print("Testing embedding generation...")
        
        embedding_model = genai.EmbeddingModel('models/embedding-001')
        result = embedding_model.embed_content(
            "Flare blockchain FTSO price feeds",
            task_type="retrieval_query"
        )
        
        print("Embedding generation successful:")
        print(f"Embedding dimensions: {len(result.embedding)}")
        print(f"Sample values: {result.embedding[:5]}...\n")
        
        print("=== Simple Test Complete ===")
        
    except ImportError:
        print("Error: google-generativeai package is not installed")
        print("Install it with: pip install google-generativeai")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_simple_gemini()
