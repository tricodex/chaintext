"""
Test script to send a query to the ChainContext API
"""
import httpx
import json
import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_query():
    """Send a test query to the API"""
    api_url = "http://localhost:8000/api/query"
    test_query = "What is the current status of the Flare network?"
    
    print(f"Sending query: {test_query}")
    print(f"API URL: {api_url}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                api_url, 
                json={"query": test_query}
            )
            
            # Check response status
            if response.status_code == 200:
                result = response.json()
                print("\n--- Response ---")
                print(f"Query ID: {result.get('query_id')}")
                print(f"Answer: {result.get('answer')}")
                print(f"Confidence: {result.get('confidence')}")
                
                # Print sources
                print("\n--- Sources ---")
                for i, source in enumerate(result.get('sources', [])):
                    print(f"[{i+1}] {source.get('source_type')} (Trust: {source.get('trust_score', 0):.2f})")
                    print(f"    {source.get('text', '')[:100]}...")
                
                # Print attestation info
                print("\n--- Attestation ---")
                attestation = result.get('attestation', {})
                print(f"Data Hash: {attestation.get('data_hash', 'N/A')}")
                print(f"Timestamp: {attestation.get('timestamp', 'N/A')}")
                print(f"Simulated: {attestation.get('simulated', True)}")
                
                print(f"\nProcessing Time: {result.get('processing_time', 0):.3f}s")
                
                # Save full response to file
                with open("test_response.json", "w") as f:
                    json.dump(result, f, indent=2)
                print("\nFull response saved to test_response.json")
                
                return True
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return False
    except Exception as e:
        print(f"Error connecting to API: {e}")
        return False

async def test_health():
    """Test the health endpoint"""
    api_url = "http://localhost:8000/api/health"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url)
            
            if response.status_code == 200:
                result = response.json()
                print("\n--- Health Check ---")
                print(f"Status: {result.get('status')}")
                print(f"Version: {result.get('version')}")
                return True
            else:
                print(f"Health check failed: {response.status_code} - {response.text}")
                return False
    except Exception as e:
        print(f"Error connecting to health endpoint: {e}")
        return False

async def main():
    """Main function to run tests"""
    # First check if the server is running
    health_ok = await test_health()
    
    if health_ok:
        # If health check passes, run the query test
        await test_query()
    else:
        print("Health check failed. Is the server running?")
        print("Start the server with: python run.py")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
