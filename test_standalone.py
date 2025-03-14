#!/usr/bin/env python3
"""
Standalone test script for ChainContext that doesn't depend on external services
Tests just the Gemini integration and the core RAG simulation
"""
import asyncio
import os
import time
import json
import hashlib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Mock classes to simulate the service dependencies
class MockRedis:
    """Mock Redis client that acts like a simple dictionary"""
    def __init__(self):
        self.data = {}
    
    async def get(self, key):
        return self.data.get(key)
    
    async def set(self, key, value, ex=None):
        self.data[key] = value
        return True
        
class MockMongoDB:
    """Mock MongoDB client with a simple collection-like interface"""
    def __init__(self):
        self.collections = {}
    
    async def __getattr__(self, name):
        if name not in self.collections:
            self.collections[name] = MockCollection()
        return self.collections[name]

class MockCollection:
    """Mock collection that stores documents in memory"""
    def __init__(self):
        self.documents = []
    
    async def insert_one(self, document):
        doc_id = hashlib.md5(str(time.time()).encode()).hexdigest()
        document['_id'] = doc_id
        self.documents.append(document)
        return MockInsertResult(doc_id)
        
    async def find(self, *args, **kwargs):
        return MockCursor(self.documents)

class MockCursor:
    """Mock cursor that simulates MongoDB query results"""
    def __init__(self, documents):
        self.documents = documents
    
    async def to_list(self, length=None):
        if length is None or length >= len(self.documents):
            return self.documents
        return self.documents[:length]
        
    def sort(self, *args, **kwargs):
        return self

class MockInsertResult:
    """Mock result of an insert operation"""
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id

class MockQdrantClient:
    """Mock Qdrant client that simulates vector search"""
    def __init__(self):
        self.collections = {}
    
    def search(self, collection_name, query_vector, limit=10):
        # Return some simulated search results
        return [
            {
                "id": f"result-{i}",
                "score": 0.9 - (i * 0.1),
                "payload": {
                    "text": f"This is simulated document {i} with relevant content about Flare blockchain",
                    "source": "flare_docs" if i % 2 == 0 else "ftso_2s",
                    "timestamp": int(time.time()) - (i * 3600),
                    "url": f"https://example.com/doc{i}"
                }
            }
            for i in range(min(limit, 5))
        ]

async def test_standalone():
    """Test ChainContext with simulated dependencies"""
    print("\n=== ChainContext Standalone Test ===\n")
    
    # Import necessary modules
    from app.core.genai import gemini_client
    
    # Check if API key is set
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY is not set in .env file")
        return
    
    # Check if Gemini client is available
    if not gemini_client.available:
        print("Error: Gemini client is not available")
        return
    
    print("1. Testing Gemini integration...")
    
    # Test content generation
    result = await gemini_client.generate_content("What is the FTSO in Flare blockchain?")
    if result["success"]:
        print("✅ Content generation successful:")
        print(f"Response: {result['text'][:200]}...\n")
    else:
        print(f"❌ Content generation failed: {result.get('text')}")
        return
    
    # Test structured content generation
    schema = {
        "answer": "string",
        "confidence": "number"
    }
    result = await gemini_client.generate_structured_content("What is the State Connector in Flare?", schema)
    if result["success"]:
        print("✅ Structured content generation successful:")
        print(f"Data: {result['data']}\n")
    else:
        print(f"❌ Structured content failed: {result.get('text')}")
        return
    
    # Test embedding generation
    embedding = await gemini_client.embed_text("Flare blockchain FTSO price feeds")
    if embedding and len(embedding) > 0:
        print("✅ Embedding generation successful:")
        print(f"Embedding dimensions: {len(embedding)}")
        print(f"Sample values: {embedding[:5]}...\n")
    else:
        print("❌ Embedding generation failed")
        return
    
    print("2. Testing simulated RAG pipeline...")
    
    # Set up mocks
    from app.services.trust import TrustScoreCalculator
    from app.services.tee import TEEAttestationGenerator
    from app.services.rag import EmbeddingService, ChainContextRAG
    
    # Initialize services with mocks
    mock_redis = MockRedis()
    mock_mongodb = MockMongoDB()
    mock_qdrant = MockQdrantClient()
    
    trust_calculator = TrustScoreCalculator()
    tee_attestation = TEEAttestationGenerator()
    embedding_service = EmbeddingService(mock_redis)
    rag_service = ChainContextRAG(
        embedding_service, 
        trust_calculator, 
        tee_attestation,
        mock_mongodb,
        mock_qdrant,
        mock_redis
    )
    
    # Test query processing
    print("Processing query: 'What is the current status of FTSO in Flare?'")
    try:
        result = await rag_service.answer_query("What is the current status of FTSO in Flare?")
        
        # Check if we got a valid response
        if "answer" in result and result["answer"]:
            print("\n✅ RAG pipeline successful:")
            print(f"Answer: {result['answer'][:200]}...\n")
            print(f"Confidence: {result['confidence']}")
            
            # Print trust scores
            print("\nTrust Scores:")
            for i, source in enumerate(result['sources'][:3]):
                print(f"Source {i+1}: {source.get('source_type', source.get('source', 'Unknown'))} (Trust: {source['trust_score']:.2f})")
            
            # Check attestation
            print("\nAttestation:")
            attestation = result['attestation']
            is_simulated = attestation.get('simulated', True)
            print(f"Type: {'Simulated' if is_simulated else 'Real TPM'}")
            print(f"Generated at: {time.ctime(attestation.get('timestamp', 0))}")
            
            print("\n✅ End-to-end test completed successfully!")
        else:
            print(f"❌ RAG pipeline failed: Invalid response format")
            if "error" in result:
                print(f"Error: {result['error']}")
            
    except Exception as e:
        print(f"❌ RAG pipeline failed with error: {e}")
    
    print("\n=== Standalone Test Complete ===")

if __name__ == "__main__":
    asyncio.run(test_standalone())
