"""Tests for the RAG system"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import json
import time

from app.services.rag import EmbeddingService, ChainContextRAG
from app.services.trust import TrustScoreCalculator
from app.services.tee import TEEAttestationGenerator

@pytest.fixture
def embedding_service():
    """Create a mock embedding service"""
    with patch.object(EmbeddingService, 'embed_text', new_callable=AsyncMock) as mock_embed:
        # Mock the embed_text method to return a fixed embedding
        mock_embed.return_value = [0.1] * 768
        
        # Create the service
        service = EmbeddingService()
        yield service

@pytest.fixture
def trust_calculator():
    """Create a trust calculator"""
    return TrustScoreCalculator()

@pytest.fixture
def tee_attestation():
    """Create a mock TEE attestation generator"""
    with patch.object(TEEAttestationGenerator, 'generate_attestation', new_callable=AsyncMock) as mock_attest:
        # Mock the generate_attestation method
        mock_attest.return_value = {
            "quote": "mock-quote",
            "data_hash": "mock-hash",
            "signature": "mock-signature",
            "timestamp": int(time.time()),
            "nonce": "mock-nonce",
            "simulated": True
        }
        
        # Create the generator
        generator = TEEAttestationGenerator()
        yield generator

@pytest.fixture
def rag_service(embedding_service, trust_calculator, tee_attestation):
    """Create a RAG service with mocked dependencies"""
    # Create mock database clients
    mock_mongodb = MagicMock()
    mock_qdrant = MagicMock()
    mock_redis = AsyncMock()
    
    # Create the service
    service = ChainContextRAG(
        embedding_service=embedding_service,
        trust_calculator=trust_calculator,
        tee_attestation=tee_attestation,
        mongodb=mock_mongodb,
        qdrant_client=mock_qdrant,
        redis_client=mock_redis
    )
    
    # Mock the _retrieve_simulated_context method
    service._retrieve_simulated_context = AsyncMock()
    service._retrieve_simulated_context.return_value = [
        {
            "id": "test-doc-1",
            "content": "This is a test document with high trust",
            "source": "flare_docs",
            "timestamp": int(time.time()) - 3600,  # 1 hour ago
            "url": "https://example.com/doc1"
        },
        {
            "id": "test-doc-2",
            "content": "This is a test document with medium trust",
            "source": "github_issues",
            "timestamp": int(time.time()) - 86400,  # 1 day ago
            "url": "https://example.com/doc2"
        }
    ]
    
    # Mock the _generate_answer method
    service._generate_answer = AsyncMock()
    service._generate_answer.return_value = {
        "answer": "This is a test answer",
        "confidence": 0.8,
        "reasoning": "This is a test reasoning"
    }
    
    yield service

@pytest.mark.asyncio
async def test_embedding_service_embed_text(embedding_service):
    """Test EmbeddingService.embed_text method"""
    # Call the method
    embedding = await embedding_service.embed_text("Test text")
    
    # Check the result
    assert len(embedding) == 768
    assert embedding[0] == 0.1

@pytest.mark.asyncio
async def test_embedding_service_cosine_similarity(embedding_service):
    """Test EmbeddingService.cosine_similarity method"""
    # Create two identical embeddings
    embedding1 = [0.1] * 768
    embedding2 = [0.1] * 768
    
    # Calculate similarity
    similarity = embedding_service.cosine_similarity(embedding1, embedding2)
    
    # Should be 1.0 for identical embeddings
    assert similarity == 1.0
    
    # Create orthogonal embeddings
    embedding1 = [1.0] + [0.0] * 767
    embedding2 = [0.0] + [1.0] + [0.0] * 766
    
    # Calculate similarity
    similarity = embedding_service.cosine_similarity(embedding1, embedding2)
    
    # Should be 0.0 for orthogonal embeddings
    assert similarity == 0.0

@pytest.mark.asyncio
async def test_rag_service_answer_query(rag_service):
    """Test ChainContextRAG.answer_query method"""
    # Call the method
    result = await rag_service.answer_query("Test query")
    
    # Check the result structure
    assert "query_id" in result
    assert "query" in result
    assert "answer" in result
    assert "confidence" in result
    assert "reasoning" in result
    assert "sources" in result
    assert "attestation" in result
    assert "processing_time" in result
    
    # Check the values
    assert result["query"] == "Test query"
    assert result["answer"] == "This is a test answer"
    assert result["confidence"] == 0.8
    assert result["reasoning"] == "This is a test reasoning"
    assert len(result["sources"]) == 2
    
    # Check that the methods were called
    rag_service._retrieve_simulated_context.assert_called_once()
    rag_service._generate_answer.assert_called_once()
    rag_service.tee_attestation.generate_attestation.assert_called_once()

@pytest.mark.asyncio
async def test_rag_service_format_sources(rag_service):
    """Test ChainContextRAG._format_sources method"""
    # Create test context
    context = [
        {
            "id": "test-doc-1",
            "text": "This is a test document with high trust",
            "source": "flare_docs",
            "timestamp": int(time.time()) - 3600,  # 1 hour ago
            "trust_score": 0.9,
            "url": "https://example.com/doc1"
        },
        {
            "id": "test-doc-2",
            "text": "This is a test document with medium trust",
            "source": "github_issues",
            "timestamp": int(time.time()) - 86400,  # 1 day ago
            "trust_score": 0.6,
            "url": "https://example.com/doc2"
        }
    ]
    
    # Format the sources
    sources = rag_service._format_sources(context)
    
    # Check the result
    assert len(sources) == 2
    assert sources[0]["source"] == "flare_docs"
    assert sources[0]["trust_score"] == 0.9
    assert sources[1]["source"] == "github_issues"
    assert sources[1]["trust_score"] == 0.6
    
    # Sources should be sorted by trust score (highest first)
    assert sources[0]["trust_score"] >= sources[1]["trust_score"]

@pytest.mark.asyncio
async def test_rag_service_build_prompt(rag_service):
    """Test ChainContextRAG._build_prompt method"""
    # Create test context
    high_trust = [
        {
            "id": "test-doc-1",
            "text": "This is a test document with high trust",
            "source": "flare_docs",
            "timestamp": int(time.time()) - 3600,  # 1 hour ago
            "trust_score": 0.9,
            "url": "https://example.com/doc1"
        }
    ]
    
    medium_trust = [
        {
            "id": "test-doc-2",
            "text": "This is a test document with medium trust",
            "source": "github_issues",
            "timestamp": int(time.time()) - 86400,  # 1 day ago
            "trust_score": 0.6,
            "url": "https://example.com/doc2"
        }
    ]
    
    # Build the prompt
    prompt = rag_service._build_prompt("Test query", high_trust, medium_trust)
    
    # Check the result
    assert "Test query" in prompt
    assert "flare_docs" in prompt
    assert "github_issues" in prompt
    assert "0.90" in prompt  # Trust score for high trust
    assert "0.60" in prompt  # Trust score for medium trust
