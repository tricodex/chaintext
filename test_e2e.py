#!/usr/bin/env python3
"""
End-to-end test for ChainContext
Tests the full pipeline without requiring external dependencies
"""
import asyncio
import os
import time
import json
import hashlib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_e2e():
    """Test the ChainContext end-to-end workflow"""
    print("\n=== ChainContext End-to-End Test ===\n")
    
    # Import modules only after environment is loaded
    from app.core.genai import gemini_client
    from app.services.trust import TrustScoreCalculator
    from app.services.tee import TEEAttestationGenerator
    from app.services.rag import EmbeddingService, ChainContextRAG
    
    # Check if API key is set
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY is not set in .env file")
        return
    
    # Initialize services
    print("Initializing services...")
    trust_calculator = TrustScoreCalculator()
    tee_attestation = TEEAttestationGenerator()
    embedding_service = EmbeddingService()
    rag_service = ChainContextRAG(embedding_service, trust_calculator, tee_attestation)
    
    # Test a query
    print("\nTesting query: 'What is FTSO in Flare blockchain?'")
    try:
        result = await rag_service.answer_query("What is FTSO in Flare blockchain?")
        
        # Print the result
        print("\n=== Query Result ===")
        print(f"Answer: {result['answer'][:200]}...\n")
        print(f"Confidence: {result['confidence']}")
        
        # Print trust scores
        print("\n=== Trust Scores ===")
        for i, source in enumerate(result['sources'][:3]):  # Show first 3 sources
            print(f"Source {i+1}: {source['source_type']} (Trust: {source['trust_score']:.2f})")
        
        # Check attestation
        print("\n=== Attestation ===")
        attestation = result['attestation']
        is_simulated = attestation.get('simulated', True)
        print(f"Attestation type: {'Simulated' if is_simulated else 'Real TPM'}")
        print(f"Generated at: {time.ctime(attestation.get('timestamp', 0))}")
        
        # Overall status
        print("\n=== Test Result ===")
        if result.get('error'):
            print(f"❌ Test failed: {result['error']}")
        else:
            print("✅ Test passed successfully!")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
    
    print("\n=== End-to-End Test Complete ===")

if __name__ == "__main__":
    asyncio.run(test_e2e())
